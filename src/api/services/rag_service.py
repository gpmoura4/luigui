from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Context,
)

from llama_index.core import SQLDatabase
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)

from llama_index.core import VectorStoreIndex

from llama_index.core.indices.struct_store.sql_query import (
    SQLTableRetrieverQueryEngine,
)

from llama_index.core.retrievers import SQLRetriever
from typing import List
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core import PromptTemplate
from llama_index.core.llms import ChatResponse

from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.bridge.pydantic import BaseModel, Field
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.schema import TextNode  # Versões mais novas (modularizadas)

from sqlalchemy import create_engine

from abc import ABC, abstractmethod
from typing import Protocol, Any

from api import schemas
from api.models import Database

import os
import openai
from core import settings

from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


class IPromptStrategy(Protocol):
    @abstractmethod
    def create_prompt(self, kwargs: Any) -> str:
        """Interface para estratégias de prompt"""
        pass


class TextToSQLPromptStrategy(IPromptStrategy):
    def __init__(self, engine):
        self.base_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
            dialect=engine.dialect.name
        )
    
    def create_prompt(self, kwargs: Any) -> str:
        return self.base_prompt.format_messages(
            query_str=kwargs["query"], schema=kwargs["context"]
        )


class ResponseSynthesisPromptStrategy(IPromptStrategy):
    def create_prompt(self, kwargs: Any) -> str:
        response_synthesis_prompt_str = (
            "Given an input question, synthesize a response from the query results.\n"
            "Query: {query_str}\n"
            "SQL: {sql_query}\n"
            "SQL Response: {context_str}\n"
            "Response: "
        )
        return PromptTemplate(
            response_synthesis_prompt_str,
        ).format_messages(
            query_str=kwargs["query_str"], 
            sql_query=kwargs["sql_query"],
            context_str=kwargs["context_str"]
        )


class PromptStrategyFactory:
    @staticmethod
    def create_text2sql_strategy(engine) -> IPromptStrategy:
        return TextToSQLPromptStrategy(engine)

    @staticmethod
    def create_synthesis_strategy() -> IPromptStrategy:
        return ResponseSynthesisPromptStrategy()


class OpenAISQLGenerator():
    def __init__(self, llm, prompt_strategy: IPromptStrategy):
        self.llm = llm
        self.prompt_strategy = prompt_strategy
    
    def change_prompt_strategy(self, new_strategy: IPromptStrategy):
        self.prompt_strategy = new_strategy
    
    def generate(self, kwargs) -> str:
        fmt_messages = self.prompt_strategy.create_prompt(kwargs)
        print("--------- generate step")
        print("\n--------- fmt_messages: ", fmt_messages)
        print("\n--------- kwargs: ", kwargs)
        return self.llm.chat(fmt_messages)


class LLMFactory:
    @staticmethod
    def create_llm(model: str):
        return OpenAI(model=model, timeout=20)


class SQLTableRetriever():
    def __init__(self, cnt_str: schemas.DatabaseConnection, tables: List[str], have_obj_index: bool):
        self.cnt_str = cnt_str
        self.tables = tables
        self.have_obj_index = have_obj_index
        self.obj_index = None
        
        engine = create_engine(f"postgresql://{self.cnt_str.username}:{self.cnt_str.password}@{self.cnt_str.host}:{self.cnt_str.port}/{self.cnt_str.name}")
        self.sql_database = SQLDatabase(engine)
    
        
        self.pgvector_store = PGVectorStore.from_params(
            database=settings.env('DB_NAME'),
            host=settings.env('DB_HOST'),
            port=settings.env('DB_PORT'),
            user=settings.env('DB_USER'),
            password=settings.env('DB_PASSWORD'),
            table_name=cnt_str.name
        )
        self.storage_context = StorageContext.from_defaults(vector_store=self.pgvector_store)

    def adding_existing_index(self, new_table_name):
        """ADICIONANDO NOVA TABELA AO PGVECTOR NUM INDEX JÁ EXISTENTE"""
        try:
            tables_info = [schemas.TableInfo(table_name=table) for table in self.tables]
            # print("\n\ntables_info schema load: ", tables_info)    
            table_schema_objs = [
                SQLTableSchema(table_name=t.table_name)
                for t in tables_info
            ]
            table_node_mapping = SQLTableNodeMapping(self.sql_database)
            index = VectorStoreIndex.from_vector_store(vector_store=self.pgvector_store)

            obj_test = ObjectIndex.from_objects_and_index(objects=table_schema_objs, object_mapping=table_node_mapping, index=index)
            
            new_table_schema = SQLTableSchema(table_name=new_table_name)
            
            new_node = table_node_mapping.to_node(new_table_schema)
        
            index.insert_nodes([new_node])
        except Exception as e:
            print(f"Erro ao carregar índice do PGVector: {e}")
            self.obj_index = None  # Evita erro caso não haja índice salvo

    def load_existing_index(self):
        """Carrega o índice existente do PGVector, se houver"""
        try:
            tables_info = [schemas.TableInfo(table_name=table) for table in self.tables]
            # print("\n\ntables_info schema load: ", tables_info)    
            table_schema_objs = [
                SQLTableSchema(table_name=t.table_name)
                for t in tables_info
            ]
            table_node_mapping = SQLTableNodeMapping(self.sql_database)
            index = VectorStoreIndex.from_vector_store(vector_store=self.pgvector_store)
            return ObjectIndex.from_objects_and_index(objects=table_schema_objs, object_mapping=table_node_mapping, index=index)
        except Exception as e:
            print(f"Erro ao carregar índice do PGVector: {e}")
            self.obj_index = None  # Evita erro caso não haja índice salvo

    def add_table_schema(self, new_table_name):
        if not self.have_obj_index:
            table_node_mapping = SQLTableNodeMapping(self.sql_database)
            tables_info = [schemas.TableInfo(table_name=new_table_name)]
            # tables_info = [schemas.TableInfo(table_name=table) for table in self.tables]
            # print("\n\ntables_info schema: ", tables_info)    
            table_schema_objs = [
                SQLTableSchema(table_name=t.table_name)
                for t in tables_info
            ]
            # print("\n\ntable_schema_objs: ", table_schema_objs)
            self.obj_index = ObjectIndex.from_objects(
                objects=table_schema_objs,
                object_mapping=table_node_mapping,
                index_cls=VectorStoreIndex,
                storage_context=self.storage_context
            )
        if self.have_obj_index:    
            self.obj_index = self.adding_existing_index(new_table_name)
            # print("self.obj_index: ", self.obj_index)
            # Se for diferente de None

    def delete_table_schema(self, table_to_delete):
        # Clear no data_vector
        self.pgvector_store.clear()

        print("-------- delete_table_schema -------")

        print("------------ Self.Tables --------------")
        print(self.tables)

        # Atualize a lista de tabelas removendo a que deve ser deletada
        print("NAME table_to_delete: ", table_to_delete)
        
        for table in self.tables:
            print("table names in self.tables: ", table)
            if table != table_to_delete:
                print("if atendido!")
                
    
        # Criando uma lista com as tabelas com nomes diferentes da que a gente está deletando
        self.tables = [table for table in self.tables if table != table_to_delete]
        
        # Recrie o índice com as tabelas restantes
        table_node_mapping = SQLTableNodeMapping(self.sql_database)
        tables_info = [schemas.TableInfo(table_name=table) for table in self.tables]
        table_schema_objs = [
            SQLTableSchema(table_name=t.table_name)
            for t in tables_info
        ]
        print("\n")
        
        for t in tables_info:
            print("Nome da tabela:", t)

        print("\n")
        print("self.storage_context:", self.storage_context)
        print("\n") 
        print("table_schema_objs:", table_schema_objs)
        print("\n") 
        
        
        self.obj_index = ObjectIndex.from_objects(
            objects=table_schema_objs,
            object_mapping=table_node_mapping,
            index_cls=VectorStoreIndex,
            storage_context=self.storage_context
        )
        
        print(f"Tabela '{table_to_delete}' removida e index atualizado.")
        
    def retrieve(self, query: str) -> List[SQLTableSchema]:    
        self.obj_index = self.load_existing_index()
        return self.obj_index.as_retriever(similarity_top_k=3, timeout=15).retrieve(query)
    
class SQLSchemaRetriever():
    def __init__(self, table_name: str):
        self.table_name = table_name

        # Nesse caso, com execção do nome do database, o resto dos campos não é obrigatório
        self.pgvector_store = PGVectorStore.from_params(
            database=settings.env('DB_NAME'),
            host=settings.env('DB_HOST'),
            port=settings.env('DB_PORT'),
            user=settings.env('DB_USER'),
            password=settings.env('DB_PASSWORD'),
            table_name=self.table_name,
        )
        self.storage_context = StorageContext.from_defaults(vector_store=self.pgvector_store)

    def adding_existing_index(self, new_table_name):
        """ADICIONANDO NOVA TABELA AO PGVECTOR NUM INDEX JÁ EXISTENTE"""
        try:
            tables_info = [schemas.TableInfo(table_name=table) for table in self.tables]
            # print("\n\ntables_info schema load: ", tables_info)    
            table_schema_objs = [
                SQLTableSchema(table_name=t.table_name)
                for t in tables_info
            ]
            table_node_mapping = SQLTableNodeMapping(self.sql_database)
            index = VectorStoreIndex.from_vector_store(vector_store=self.pgvector_store)

            obj_test = ObjectIndex.from_objects_and_index(objects=table_schema_objs, object_mapping=table_node_mapping, index=index)
            
            new_table_schema = SQLTableSchema(table_name=new_table_name)
            
            new_node = table_node_mapping.to_node(new_table_schema)
        
            index.insert_nodes([new_node])
        except Exception as e:
            print(f"Erro ao carregar índice do PGVector: {e}")
            self.obj_index = None  # Evita erro caso não haja índice salvo

    def load_existing_index(self):
        """Carrega o índice existente do PGVector, se houver"""
        try:
            tables_info = [schemas.TableInfo(table_name=table) for table in self.tables]
            # print("\n\ntables_info schema load: ", tables_info)    
            table_schema_objs = [
                SQLTableSchema(table_name=t.table_name)
                for t in tables_info
            ]
            table_node_mapping = SQLTableNodeMapping(self.sql_database)
            index = VectorStoreIndex.from_vector_store(vector_store=self.pgvector_store)
            return ObjectIndex.from_objects_and_index(objects=table_schema_objs, object_mapping=table_node_mapping, index=index)
        except Exception as e:
            print(f"Erro ao carregar índice do PGVector: {e}")
            self.obj_index = None  # Evita erro caso não haja índice salvo

    def add_table_schema(self, new_table_schema):
        # Criar um nó de texto com o schema fornecido
        node = TextNode(
            text=new_table_schema,
            metadata={
                "table_name": self.table_name,
                "type": "schema_definition"
            }
        )
        
        # Criar ou carregar o índice existente
        index = VectorStoreIndex.from_vector_store(
            vector_store=self.pgvector_store
            # service_context=ServiceContext.from_defaults(
            #     embed_model=Settings.embed_model  # Assume configuração prévia do embed_model
            # )
        )
        
        # Inserir o nó no índice
        index.insert_nodes([node])
        
        # Opcional: persistir as alterações no armazenamento
        # self.pgvector_store.persist(persist_dir=f"storage/{self.table_name}")
            

    def delete_table_schema(self, table_to_delete):
        # Clear no data_vector
        self.pgvector_store.clear()

        print("-------- delete_table_schema -------")

        print("------------ Self.Tables --------------")
        print(self.tables)

        # Atualize a lista de tabelas removendo a que deve ser deletada
        print("NAME table_to_delete: ", table_to_delete)
        
        for table in self.tables:
            print("table names in self.tables: ", table)
            if table != table_to_delete:
                print("if atendido!")
                
    
        # Criando uma lista com as tabelas com nomes diferentes da que a gente está deletando
        self.tables = [table for table in self.tables if table != table_to_delete]
        
        # Recrie o índice com as tabelas restantes
        table_node_mapping = SQLTableNodeMapping(self.sql_database)
        tables_info = [schemas.TableInfo(table_name=table) for table in self.tables]
        table_schema_objs = [
            SQLTableSchema(table_name=t.table_name)
            for t in tables_info
        ]
        print("\n")
        
        for t in tables_info:
            print("Nome da tabela:", t)

        print("\n")
        print("self.storage_context:", self.storage_context)
        print("\n") 
        print("table_schema_objs:", table_schema_objs)
        print("\n") 
        
        
        self.obj_index = ObjectIndex.from_objects(
            objects=table_schema_objs,
            object_mapping=table_node_mapping,
            index_cls=VectorStoreIndex,
            storage_context=self.storage_context
        )
        
        print(f"Tabela '{table_to_delete}' removida e index atualizado.")
        
    def retrieve(self, query: str) -> List[SQLTableSchema]:    
        self.obj_index = self.load_existing_index()
        return self.obj_index.as_retriever(similarity_top_k=3, timeout=15).retrieve(query)


    


# Class que executa as querys no banco
class SQLRunQuery():
    def __init__(self, sql_database):
        self.sql_executor = SQLRetriever(sql_database)


class TextToSQLWorkflow(Workflow):
    """Text-to-SQL Workflow that does query-time table retrieval."""

    def __init__(
        self,
        obj_retriever: SQLTableRetriever,
        sql_run_query: SQLRunQuery,
        sql_generator: OpenAISQLGenerator,
        sql_database,
        *args,
        **kwargs,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs, timeout=30)
        self.obj_retriever = obj_retriever
        self.sql_run_query = sql_run_query
        self.sql_generator = sql_generator
        self.sql_database = sql_database
    
    @step
    def retrieve_tables(
        self, ctx: Context, ev: StartEvent
    ) -> schemas.TableRetrieveEvent:
        """Retrieve tables."""
        # print("--------- retrieve_tables step test")
        table_schema_objs = self.obj_retriever.retrieve(ev.query)
        table_context_str = self._get_table_context_str(table_schema_objs)

        print(" ---------------- retrieve_tables return:", schemas.TableRetrieveEvent(
            table_context_str=table_context_str, query=ev.query))

        return schemas.TableRetrieveEvent(
            table_context_str=table_context_str, query=ev.query
        )
    
    @step
    def generate_sql(
        self, ctx: Context, ev: schemas.TableRetrieveEvent
    ) -> schemas.TextToSQLEvent:
        """Generate SQL statement."""
        # print("--------- generate_sql step test")
        kwargs = {
            "context": ev.table_context_str,
            "query": ev.query,
        }
        chat_response = self.sql_generator.generate(kwargs)
        sql = self._parse_response_to_sql(chat_response)
        print(" ---------------- generate_sql return:", schemas.TextToSQLEvent(sql=sql, query=ev.query))
        return schemas.TextToSQLEvent(sql=sql, query=ev.query)
    
    @step
    def generate_response(self, ctx: Context, ev: schemas.TextToSQLEvent) -> StopEvent:
        # print("--------- generate_response step test")
        """Run SQL retrieval and generate response."""
        
        #Executar a query no banco
        query_response = self.sql_run_query.sql_executor.retrieve(ev.sql)
        print("\nretrieved_schemas: ",query_response)
        self.sql_generator.change_prompt_strategy(PromptStrategyFactory.create_synthesis_strategy())
        print("\nself.sql_generator: ",self.sql_generator)
        kwargs = {
            "query_str": ev.query, 
            "sql_query": ev.sql,
            "context_str": query_response,
        }
        chat_response = self.sql_generator.generate(kwargs)
        response_text = chat_response.message.content
        print("\n chat_response: ",chat_response)
        print("\n chat_response TIPO: ", type(chat_response))
        print("\n chat_response dir: ", dir(chat_response))
        print(" ---------------- generate_response return:", StopEvent(result=response_text))
    

        result = schemas.WorkFlowResult(sql_query=ev.sql,response=response_text)
        return StopEvent(result=result)

    def _get_table_context_str(self, table_schema_objs: List[SQLTableSchema]) -> str:
        """Get table context string."""
        # print("--------- _get_table_context_str step test")
        context_strs = []
        for table_schema_obj in table_schema_objs:
            table_info = self.sql_database.get_single_table_info(
                table_schema_obj.table_name
            )
            if table_schema_obj.context_str:
                table_opt_context = " The table description is: "
                table_opt_context += table_schema_obj.context_str
                table_info += table_opt_context

            context_strs.append(table_info)
            print(" ---------------- _get_table_context_str return:", "\n\n".join(context_strs))
        return "\n\n".join(context_strs)
    
    def _parse_response_to_sql(self, chat_response: ChatResponse) -> str:
        """Parse response to SQL."""
        response = chat_response.message.content
        sql_query_start = response.find("SQLQuery:")
    
        if sql_query_start != -1:
            response = response[sql_query_start:].removeprefix("SQLQuery:")
    
        sql_result_start = response.find("SQLResult:")
        if sql_result_start != -1:
            response = response[:sql_result_start]

        # Garantir remoção completa dos caracteres ```
        response = response.strip()
        if response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()

        print(" ---------------- _parse_response_to_sql return:", response)
        return response

    

async def starts_workflow(
        cnt_str: schemas.DatabaseConnection, 
        tables: List[str], 
        user_question: str, 
        have_obj_index: bool
        ) -> schemas.WorkFlowResult:
    engine = create_engine(f"postgresql://{cnt_str.username}:{cnt_str.password}@{cnt_str.host}:{cnt_str.port}/{cnt_str.name}")
    sql_database = SQLDatabase(engine)

    obj_retriever = SQLTableRetriever(
        cnt_str=cnt_str,
        tables=tables,
        have_obj_index=have_obj_index
    )

    print("obj_retriever", obj_retriever)

    sql_run_query = SQLRunQuery(
        sql_database=sql_database
    )

    print("sql_run_query", sql_run_query)

    llm=LLMFactory.create_llm("gpt-4o")
    prompt_strategy=TextToSQLPromptStrategy(engine)

    sql_generator = OpenAISQLGenerator(
        llm=llm,
        prompt_strategy=prompt_strategy
    )

    print("sql_generator", sql_generator)

    txt_tosql_workflow = TextToSQLWorkflow(
        obj_retriever=obj_retriever,
        sql_run_query=sql_run_query,
        sql_generator=sql_generator,
        sql_database=sql_database
    )

    print("txt_tosql_workflow", txt_tosql_workflow)

    response = await txt_tosql_workflow.run(
        query=user_question,
        timeout=30
        )

    print("\n\nResponse: ", response.sql_query)
    print("\n\n")

    return response

def generate_postgres_schemas(json_data):
    # Agrupa as colunas por (schema, tabela)    
    tables = {}
    for entry in json_data:
        schema = entry['schema_name']
        table = entry['table_name']
        column = entry['column_name']
        column_type = entry['column_type']
        
        key = (schema, table)
        if key not in tables:
            tables[key] = []
        tables[key].append(f'    "{column}" {column_type}')
    
    # Gera os comandos SQL para cada tabela e os armazena numa lista
    schemas = []
    for (schema, table), columns in tables.items():
        sql = f'CREATE SCHEMA IF NOT EXISTS "{schema}";\n'
        sql += f'CREATE TABLE IF NOT EXISTS "{schema}"."{table}" (\n'
        sql += ",\n".join(columns)
        sql += "\n);"
        schemas.append({"schema": sql, "table_name": table})
    
    return schemas


# json = [{"schema_name" : "public", "table_name" : "data_vector", "column_name" : "embedding", "column_type" : "USER-DEFINED"}, {"schema_name" : "public", "table_name" : "sec_text_chunk", "column_name" : "page_label", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_group_permissions", "column_name" : "group_id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_group_permissions", "column_name" : "permission_id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_user_groups", "column_name" : "id", "column_type" : "bigint"}, {"schema_name" : "public", "table_name" : "auth_user_groups", "column_name" : "user_id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_user_groups", "column_name" : "group_id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_user_user_permissions", "column_name" : "id", "column_type" : "bigint"}, {"schema_name" : "public", "table_name" : "auth_user_user_permissions", "column_name" : "user_id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_user_user_permissions", "column_name" : "permission_id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "last_login", "column_type" : "timestamp with time zone"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "is_superuser", "column_type" : "boolean"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "is_staff", "column_type" : "boolean"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "is_active", "column_type" : "boolean"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "date_joined", "column_type" : "timestamp with time zone"}, {"schema_name" : "public", "table_name" : "django_admin_log", "column_name" : "id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "django_admin_log", "column_name" : "action_time", "column_type" : "timestamp with time zone"}, {"schema_name" : "public", "table_name" : "django_admin_log", "column_name" : "action_flag", "column_type" : "smallint"}, {"schema_name" : "public", "table_name" : "django_admin_log", "column_name" : "content_type_id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "django_admin_log", "column_name" : "user_id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "django_session", "column_name" : "expire_date", "column_type" : "timestamp with time zone"}, {"schema_name" : "public", "table_name" : "api_database", "column_name" : "id", "column_type" : "bigint"}, {"schema_name" : "public", "table_name" : "api_database", "column_name" : "port", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "api_database", "column_name" : "have_obj_index", "column_type" : "boolean"}, {"schema_name" : "public", "table_name" : "api_database", "column_name" : "user_id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "api_questionanswer", "column_name" : "id", "column_type" : "bigint"}, {"schema_name" : "public", "table_name" : "api_questionanswer", "column_name" : "database_id", "column_type" : "bigint"}, {"schema_name" : "public", "table_name" : "api_table", "column_name" : "id", "column_type" : "bigint"}, {"schema_name" : "public", "table_name" : "api_table", "column_name" : "database_id", "column_type" : "bigint"}, {"schema_name" : "public", "table_name" : "city_stats", "column_name" : "population", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "city_stats2", "column_name" : "population", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "data_vector", "column_name" : "id", "column_type" : "bigint"}, {"schema_name" : "public", "table_name" : "data_vector", "column_name" : "metadata_", "column_type" : "json"}, {"schema_name" : "public", "table_name" : "sec_text_chunk", "column_name" : "id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "sec_text_chunk", "column_name" : "embedding", "column_type" : "USER-DEFINED"}, {"schema_name" : "public", "table_name" : "django_migrations", "column_name" : "id", "column_type" : "bigint"}, {"schema_name" : "public", "table_name" : "django_migrations", "column_name" : "applied", "column_type" : "timestamp with time zone"}, {"schema_name" : "public", "table_name" : "django_content_type", "column_name" : "id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_permission", "column_name" : "id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_permission", "column_name" : "content_type_id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_group", "column_name" : "id", "column_type" : "integer"}, {"schema_name" : "public", "table_name" : "auth_group_permissions", "column_name" : "id", "column_type" : "bigint"}, {"schema_name" : "public", "table_name" : "sec_text_chunk", "column_name" : "file_name", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "sec_text_chunk", "column_name" : "text", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "api_database", "column_name" : "host", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "city_stats", "column_name" : "city_name", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "django_migrations", "column_name" : "app", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "django_migrations", "column_name" : "name", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "data_vector", "column_name" : "node_id", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "city_stats", "column_name" : "country", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "django_content_type", "column_name" : "app_label", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "django_content_type", "column_name" : "model", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "api_questionanswer", "column_name" : "question", "column_type" : "text"}, {"schema_name" : "public", "table_name" : "auth_permission", "column_name" : "name", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "django_admin_log", "column_name" : "object_id", "column_type" : "text"}, {"schema_name" : "public", "table_name" : "auth_permission", "column_name" : "codename", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "django_admin_log", "column_name" : "object_repr", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "auth_group", "column_name" : "name", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "api_questionanswer", "column_name" : "answer", "column_type" : "text"}, {"schema_name" : "public", "table_name" : "django_admin_log", "column_name" : "change_message", "column_type" : "text"}, {"schema_name" : "public", "table_name" : "api_questionanswer", "column_name" : "query", "column_type" : "text"}, {"schema_name" : "public", "table_name" : "city_stats2", "column_name" : "city_name", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "django_session", "column_name" : "session_key", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "django_session", "column_name" : "session_data", "column_type" : "text"}, {"schema_name" : "public", "table_name" : "data_vector", "column_name" : "text", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "api_table", "column_name" : "name", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "api_database", "column_name" : "name", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "api_database", "column_name" : "username", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "password", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "api_database", "column_name" : "password", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "city_stats2", "column_name" : "country", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "username", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "first_name", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "last_name", "column_type" : "character varying"}, {"schema_name" : "public", "table_name" : "auth_user", "column_name" : "email", "column_type" : "character varying"}]

# schemas = generate_postgres_schemas(json)
# print(schemas)