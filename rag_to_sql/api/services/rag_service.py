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

from sqlalchemy import create_engine

from abc import ABC, abstractmethod
from typing import Protocol, Any

from api import schemas
from api.models import Database

import os
import openai

from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


class IPromptStrategy(Protocol):
    @abstractmethod
    def create_prompt(self, **kwargs: Any) -> str:
        """Interface para estratégias de prompt"""
        pass


class TextToSQLPromptStrategy(IPromptStrategy):
    def __init__(self, engine):
        self.base_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
            dialect=engine.dialect.name
        )
    
    def create_prompt(self, **kwargs: Any) -> str:
        return self.base_prompt.format_messages(
            query_str=kwargs["query"], schema=kwargs["context"]
        )


class ResponseSynthesisPromptStrategy(IPromptStrategy):
    def create_prompt(self, **kwargs: Any) -> str:
        response_synthesis_prompt_str = (
            "Given an input question, synthesize a response from the query results.\n"
            "Query: {query_str}\n"
            "SQL: {sql_query}\n"
            "SQL Response: {context_str}\n"
            "Response: "
        )
        return PromptTemplate(
            response_synthesis_prompt_str,
        ).format_messages(**kwargs)


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
    
    def generate(self, context: str, query: str) -> str:
        fmt_messages = self.prompt_strategy.create_prompt(context, query)
        return self.llm.chat(fmt_messages)


class LLMFactory:
    @staticmethod
    def create_llm(model: str):
        return OpenAI(model=model)


class SQLTableRetriever():
    def __init__(self, cnt_str: schemas.DatabaseConnection, tables: List[str], have_obj_index: bool):
        self.cnt_str = cnt_str
        self.tables = tables
        self.have_obj_index = have_obj_index
        self.obj_index = None
        
        engine = create_engine(f"postgresql://{self.cnt_str.username}:{self.cnt_str.password}@{self.cnt_str.host}:{self.cnt_str.port}/{self.cnt_str.name}")
        self.sql_database = SQLDatabase(engine)
    
        
        self.pgvector_store = PGVectorStore.from_params(
            database=cnt_str.name,
            host=cnt_str.host,
            port=cnt_str.port,
            user=cnt_str.username,
            password=cnt_str.password,
            table_name=""+cnt_str.name
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
            
            # query_engine = SQLTableRetrieverQueryEngine(
            #     self.sql_database, obj_test.as_retriever(similarity_top_k=1)
            # )

            # response = query_engine.query("Qual o funcionário com o maior salário?") 
            # print("\rResponse: ", response)
            # print("\nObj_test: ", obj_test)

            # Cria uma nova instância de SQLTableSchema para a nova tabela
            # Cria a instância para a nova tabela
            new_table_schema = SQLTableSchema(table_name=new_table_name)
            # Converte o novo objeto para um nó usando o mapeamento
            new_node = table_node_mapping.to_node(new_table_schema)
            # Insere o novo nó diretamente no índice
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
        


    # def delete_table_schema(self, table_to_delete):
    #     print("-------- delete_table_schema -------")
    #     # tables_info = [schemas.TableInfo(table_name=table) for table in self.tables]
        
    #     # table_schema_objs = [
    #     #     SQLTableSchema(table_name=t.table_name)
    #     #     for t in tables_info
    #     # ]
    #     table_node_mapping = SQLTableNodeMapping(self.sql_database)

    #     # self.pgvector_store = PGVectorStore.from_params(
    #     #     database=cnt_str.name,
    #     #     host=cnt_str.host,
    #     #     port=cnt_str.port,
    #     #     user=cnt_str.username,
    #     #     password=cnt_str.password,
    #     #     table_name=""+cnt_str.name
    #     # )
    #     # self.storage_context = StorageContext.from_defaults(vector_store=self.pgvector_store)

        
        

    #     # index = VectorStoreIndex.from_vector_store(vector_store=self.pgvector_store)

    #     # obj_test = ObjectIndex.from_objects_and_index(
    #     #     objects=table_schema_objs,
    #     #     object_mapping=table_node_mapping,
    #     #     index=index
    #     # )
                        
    #     # Cria a instância para a tabela que deseja deletar
    #     new_table_schema = SQLTableSchema(table_name=table_to_delete)
    #     # Converte o objeto para um nó usando o mapeamento
    #     node = table_node_mapping.to_node(new_table_schema)
    #     print("delete node function deletará o nó:", node)
    #     # Extraia o identificador do nó (supondo que seja o atributo 'id_')
    #     node_id = node.id_
    #     # Deleta o nó diretamente no índice usando o identificador\

    #     # index.delete([node_id])
    #     self.pgvector_store.clear()
    #     print("delete node function delete sucess!")
    


# Class que executa as querys no banco
class SQLRunQuery():
    def __init__(self, sql_database):
        self.sql_executor = SQLRetriever(sql_database)


class TextToSQLWorkflow(Workflow):
    """Text-to-SQL Workflow that does query-time table retrieval."""

    def __init__(
        self,
        obj_retriever: SQLTableRetriever,
        sql_executor: SQLRunQuery,
        sql_generator: OpenAISQLGenerator,
        sql_database,
        *args,
        **kwargs,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self.obj_retriever = obj_retriever
        self.sql_executor = sql_executor
        self.sql_generator = sql_generator
        self.sql_database = sql_database
    
    @step
    def retrieve_tables(
        self, ctx: Context, ev: StartEvent
    ) -> schemas.TableRetrieveEvent:
        """Retrieve tables."""
        table_schema_objs = self.obj_retriever.retrieve(ev.query)
        table_context_str = self._get_table_context_str(table_schema_objs)
        return schemas.TableRetrieveEvent(
            table_context_str=table_context_str, query=ev.query
        )
    
    @step
    def generate_sql(
        self, ctx: Context, ev: schemas.TableRetrieveEvent
    ) -> schemas.TextToSQLEvent:
        """Generate SQL statement."""
        kwargs = {
            "context": ev.table_context_str,
            "query": ev.query,
        }
        chat_response = self.sql_generator.generate(kwargs)
        sql = self._parse_response_to_sql(chat_response)
        return schemas.TextToSQLEvent(sql=sql, query=ev.query)
    
    @step
    def generate_response(self, ctx: Context, ev: schemas.TextToSQLEvent) -> StopEvent:
        """Run SQL retrieval and generate response."""
        #Executar a query no banco
        retrieved_rows = self.sql_retriever.retrieve(ev.sql)
        self.sql_generator.change_prompt_strategy(PromptStrategyFactory.create_synthesis_strategy())
        kwargs = {
            "query_str": ev.query,
            "sql_query": ev.sql,
            "context_str": retrieved_rows,
        }
        chat_response = self.sql_generator.generate(kwargs)
        return StopEvent(result=chat_response)

    def _get_table_context_str(self, table_schema_objs: List[SQLTableSchema]) -> str:
        """Get table context string."""
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
        return "\n\n".join(context_strs)
    
    def _parse_response_to_sql(self, chat_response: ChatResponse) -> str:
        """Parse response to SQL."""
        response = chat_response.message.content
        sql_query_start = response.find("SQLQuery:")
        if sql_query_start != -1:
            response = response[sql_query_start:]
            # TODO: move to removeprefix after Python 3.9+
            if response.startswith("SQLQuery:"):
                response = response[len("SQLQuery:") :]
        sql_result_start = response.find("SQLResult:")
        if sql_result_start != -1:
            response = response[:sql_result_start]
        return response.strip().strip("```").strip()
    