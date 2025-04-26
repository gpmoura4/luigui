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
# from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.schema import TextNode  # Versões mais novas (modularizadas)

from sqlalchemy import create_engine

from abc import ABC, abstractmethod
from typing import Protocol, Any

from api import schemas
from api.models import Database

import os
from openai import OpenAI
from core import settings

from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

OpenAI.api_key = os.getenv("OPENAI_API_KEY")


class IPromptStrategy(Protocol):
    @abstractmethod
    def create_prompt(self, kwargs: Any) -> str:
        """Interface para estratégias de prompt"""
        pass

    def function_name(self) -> str:
        """Nome da função para function-calling."""
        pass

    def function_schema(self) -> dict:
        """JSON Schema dos parâmetros de saída."""
        pass



class TextToSQLPromptStrategy(IPromptStrategy):
    def __init__(self, engine):
        self.base_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(dialect=engine)

    def create_prompt(self, kwargs: Any) -> str:
        return self.base_prompt.format_messages(query_str=kwargs["query"], schema=kwargs["context"])

    def function_name(self) -> str:
        return "text_to_sql"

    def function_schema(self) -> dict:
        return schemas.TextToSQLEvent.model_json_schema()
    
class SchemaSummaryPromptStrategy(IPromptStrategy):
    def __init__(self, database):
        self.database = database

    def create_prompt(self, kwargs: Any) -> str:
        schema_summary_prompt = (
            "Give me a short, concise summary/caption of the table in the following table schema. \n"
            "Schema Information:\n{context}\n"
            "Answer: \n"
        )
        return PromptTemplate(
            schema_summary_prompt,
        ).format_messages(
            context=kwargs["context"],
        )
    

class OptimizesSQLQueryPromptStrategy(IPromptStrategy):
    def __init__(self, database):

        self.database=database
    
    def create_prompt(self, kwargs: Any) -> str:
        optimize_sql_query_prompt = (
            "Optimize the following SQL query for better performance. Return the optimized sql query and an explanation. \n"
            "Schema Information:\n{context}\n"
            "Database: {database}\n" 
            "Query: {query}\n"
            "Answer: \n"
        )
        return PromptTemplate(
            optimize_sql_query_prompt,
        ).format_messages(
            query=kwargs["query"],
            context=kwargs["context"],
            database=self.database,
        )
    
    def function_name(self) -> str:
        return "optimize_sql"

    def function_schema(self) -> dict:
        return schemas.OptimizeResult.model_json_schema()
    

class ExplainSQLQueryPromptStrategy(IPromptStrategy):
    def __init__(self, database):

        self.database=database
    
    def create_prompt(self, kwargs: Any) -> str:
        explain_sql_query_prompt = (
            "Explain this SQL query in detail; do not return the provided query, but only an explanation of what it does. \n"
            "Schema Information:\n{context}\n"
            "Database: {database}\n" 
            "Query: {query}\n"
            "Explanation: \n"
        )
        return PromptTemplate(
            explain_sql_query_prompt,
        ).format_messages(
            query=kwargs["query"],
            context=kwargs["context"],
            database=self.database,
        )
    
    def function_name(self) -> str:
        return "explain_sql"

    def function_schema(self) -> dict:
        return schemas.ExplainSQLResult.model_json_schema()
    

class FixSQLQueryPromptStrategy(IPromptStrategy):
    def __init__(self, database):

        self.database=database
    
    def create_prompt(self, kwargs: Any) -> str:
        optimize_sql_query_prompt = (
            "Fix the SQL syntax errors in the following query. Answer only with a single formatted SQL code block, no additional text. The Query: \n"
            "Schema Information:\n{context}\n"
            "Database: {database}\n" 
            "Query: {query}\n"
            "Answer: \n"
        )
        return PromptTemplate(
            optimize_sql_query_prompt,
        ).format_messages(
            query=kwargs["query"],
            context=kwargs["context"],
            database=self.database,
        )
    
    def function_name(self) -> str:
        return "fix_sql"

    def function_schema(self) -> dict:
        return schemas.FixSQLResult.model_json_schema()

    
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
    
    def function_name(self) -> str:
        return "synthesize_response"

    def function_schema(self) -> dict:
        return schemas.SynthesisResult.model_json_schema()


class PromptStrategyFactory:
    @staticmethod
    def create_text2sql_strategy(engine) -> IPromptStrategy:
        return TextToSQLPromptStrategy(engine)

    @staticmethod
    def create_synthesis_strategy() -> IPromptStrategy:
        return ResponseSynthesisPromptStrategy()
    
    @staticmethod
    def create_optimizesql_strategy(database) -> IPromptStrategy:
        return OptimizesSQLQueryPromptStrategy(database)
    
    @staticmethod
    def create_explainsql_strategy(database) -> IPromptStrategy:
        return ExplainSQLQueryPromptStrategy(database)
    
    @staticmethod
    def create_fixsql_strategy(database) -> IPromptStrategy:
        return FixSQLQueryPromptStrategy(database)
    @staticmethod
    def create_schema_summary_strategy(database) -> IPromptStrategy:
        return SchemaSummaryPromptStrategy(database)


class OpenAISQLGenerator:
    def __init__(self, llm, prompt_strategy: IPromptStrategy):
        self.llm = llm
        self.prompt_strategy = prompt_strategy

    def change_prompt_strategy(self, new_strategy: IPromptStrategy):
        self.prompt_strategy = new_strategy

    def generate(self, kwargs) -> BaseModel:
        # 1. Cria o prompt de sistema/usuário
        user_message = {
            "role": "user",
            "content": str(self.prompt_strategy.create_prompt(kwargs))
        }

        # 2. Função “simulada” para structured output
        func_def = {
            "name": self.prompt_strategy.function_name(),
            "description": f"Structured output for {self.prompt_strategy.function_name()}",
            "parameters": self.prompt_strategy.function_schema()
        }

        # 3. Chama a ChatCompletion com function-calling
        response = self.llm.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[user_message],
            functions=[func_def],
            function_call={"name": self.prompt_strategy.function_name()},
        )

        # 4. Extrai o JSON retornado e valida com Pydantic
        func_call = response.choices[0].message.function_call
        result_json = func_call.arguments
        result_model = {
            "text_to_sql": schemas.TextToSQLEvent,
            "synthesize_response": schemas.SynthesisResult,
            "optimize_sql": schemas.OptimizeResult,
            "explain_sql": schemas.ExplainSQLResult,
            "fix_sql": schemas.FixSQLResult,
        }[self.prompt_strategy.function_name()]
        print("\n\n\nResultModel: ", result_model.model_validate_json(result_json))
        return result_model.model_validate_json(result_json)
    
    def generate_schema_summary(self, kwargs) -> BaseModel:

        user_message = {
            "role": "user",
            "content": str(self.prompt_strategy.create_prompt(kwargs))
        }

        response = self.llm.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[user_message],
        response_format=schemas.SchemaSummary,
        )

        print("================================\n")
        print(response.choices[0].message)
        print("Tipo: ", type(response.choices[0].message))
        print("================================\n")
        
        return schemas.SchemaSummary.model_validate_json(response.choices[0].message.content)



class LLMFactory:
    @staticmethod
    def create_llm(model: str):
        client = OpenAI()
        return client


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
    def __init__(self, db_name: str, sql_generator: OpenAISQLGenerator):
        self.db_name = db_name
        self.sql_generator = sql_generator
        # Nesse caso, com execção do nome do database, o resto dos campos não é obrigatório
        self.pgvector_store = PGVectorStore.from_params(
            database=settings.env('DB_NAME'),
            host=settings.env('DB_HOST'),
            port=settings.env('DB_PORT'),
            user=settings.env('DB_USER'),
            password=settings.env('DB_PASSWORD'),
            table_name=self.db_name,
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
            return VectorStoreIndex.from_vector_store(vector_store=self.pgvector_store)
        except Exception as e:
            print(f"Erro ao carregar índice do PGVector: {e}")
            self.pgvector_store = None  # Evita erro caso não haja índice salvo

    def add_table_schema(self, table_name, table_schema):
        # Criar um nó de texto com o schema fornecido
        # Levar o table_schema pro LLM produzir um summary

        kwargs = {
            "context": table_schema
        }
        
        schema_summary_result = self.sql_generator.generate_schema_summary(kwargs)
    
        node = TextNode(
            text=table_schema,
            metadata={
                "table_name": table_name,
                "type": "schema_definition",
                "schema_summary": schema_summary_result.schema_summary
            },
            schema_summary=schema_summary_result.schema_summary
        )
        
        # Criar ou carregar o índice existente
        index = VectorStoreIndex.from_vector_store(
            vector_store=self.pgvector_store
        )
        
        # Inserir o nó no índice
        index.insert_nodes([node])
                  

    def delete_table_schema(self, table_name):
        """
        Remove os nós correspondentes ao schema da tabela com base no metadado "table_name".
        """
        try:
            index = VectorStoreIndex.from_vector_store(vector_store=self.pgvector_store)
            
            # Acessa o index_struct (atributo protegido) para obter o mapping de nós
            index_struct = index._index_struct
            
            # Recupera os node_ids presentes no índice
            node_ids = list(index_struct.nodes_dict.values())
            
            # Recupera os nós armazenados no docstore
            nodes = index._docstore.get_nodes(node_ids)
            
            # Filtra os nós que possuem o metadado "table_name" correspondente
            nodes_to_delete = [node.node_id for node in nodes if node.metadata.get("table_name") == table_name]
            
            if nodes_to_delete:
                # Remove os nós do vector store usando o método delete_nodes do índice
                index.delete_nodes(nodes_to_delete)
                
                # Opcionalmente, remova também do index_struct e docstore
                for node_id in nodes_to_delete:
                    index_struct.delete(node_id)
                    index._docstore.delete_document(node_id, raise_error=False)
        except Exception as e:
            print(f"Erro ao deletar schema do PGVector: {e}")


        
    def retrieve(self, query: str) -> List[SQLTableSchema]:    
        self.pgvector_store = self.load_existing_index()
        return self.pgvector_store.as_retriever(similarity_top_k=3, timeout=15).retrieve(query)



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
        prompt_type: str,
        *args,
        **kwargs,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs, timeout=30)
        self.obj_retriever = obj_retriever
        self.sql_run_query = sql_run_query
        self.sql_generator = sql_generator
        self.sql_database = sql_database
        self.prompt_type = prompt_type
    
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
    ) -> schemas.TextToSQLEvent | StopEvent:
        """Generate SQL statement."""
        kwargs = {
            "context": ev.table_context_str,
            "query": ev.query,
        }
        match self.prompt_type:
            case "text_to_sql":
                response_event = self.sql_generator.generate(kwargs)
                return response_event

            case "optimize_sql":
                chat_response = self.sql_generator.generate(kwargs)
                response = schemas.SynthesisResult(
                    natural_language_response=chat_response.optimization_explanation,
                    sql_query=chat_response.optimized_query
                )
                return StopEvent(result=response)
            
            case "explain_sql":
                chat_response = self.sql_generator.generate(kwargs)
                response = schemas.SynthesisResult(
                    natural_language_response=chat_response.sql_query_explanation,
                    sql_query=""
                )
                return StopEvent(result=response)
            
            case "fix_sql":
                chat_response = self.sql_generator.generate(kwargs)
                response = schemas.SynthesisResult(
                    natural_language_response=chat_response.fix_explanation,
                    sql_query=chat_response.fixed_sql_query
                )
                return StopEvent(result=response)

            case _:
                raise ValueError(f"Unknown prompt_type: {self.prompt_type}")

    
    @step
    def generate_response(self, ctx: Context, ev: schemas.TextToSQLEvent) -> StopEvent:
        # print("--------- generate_response step test")
        """Run SQL retrieval and generate response."""
        
        #Executar a query no banco
        query_response = self.sql_run_query.sql_executor.retrieve(ev.sql_query)
        print("\nretrieved_schemas: ",query_response)
        self.sql_generator.change_prompt_strategy(PromptStrategyFactory.create_synthesis_strategy())
        print("\nself.sql_generator: ",self.sql_generator)
        kwargs = {
            "query_str": ev.natural_language_query, 
            "sql_query": ev.sql_query,
            "context_str": query_response,
        }
        response_event = self.sql_generator.generate(kwargs)
        print("\n\nchat_response: ", response_event)

        # result = schemas.SynthesisResult(sql_query=ev.sql, natural_language_response=response_text)
        return StopEvent(result=response_event)

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
    
    
class SimpleTextToSQLWorkflow(Workflow):
    """Text-to-SQL Workflow that does query-time table retrieval."""

    def __init__(
        self,
        schema_retriever: SQLSchemaRetriever,    
        sql_generator: OpenAISQLGenerator,
        prompt_type: str,
        *args,
        **kwargs,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs, timeout=300)
        self.schema_retriever = schema_retriever
        self.sql_generator = sql_generator
        self.prompt_type = prompt_type
    
    @step
    def retrieve_tables(
        self, ctx: Context, ev: StartEvent
    ) -> schemas.SchemaRetrieveEvent:
        """Retrieve tables."""
    
        retrieved_schemas = self.schema_retriever.retrieve(ev.query)

        table_schema = "\n\n".join(schema.text for schema in retrieved_schemas)

        # Retornando o schema e a pergunta do usuário
        return schemas.SchemaRetrieveEvent(
            table_schema=table_schema, query=ev.query
        )
    
    @step
    def generate_sql(
        self, ctx: Context, ev: schemas.SchemaRetrieveEvent
    ) -> StopEvent:
        """Generate SQL statement."""
        print("--------- generate_sql step test 1")
        kwargs = {
            "context": ev.table_schema,
            "query": ev.query,
        }

        match self.prompt_type:
            case "text_to_sql":
                chat_response = self.sql_generator.generate(kwargs)
                response = schemas.SynthesisResult(
                    natural_language_response="",
                    sql_query=chat_response.sql_query
                )
                return StopEvent(result=response)

            case "optimize_sql":
                chat_response = self.sql_generator.generate(kwargs)
                response = schemas.SynthesisResult(
                    natural_language_response=chat_response.optimization_explanation,
                    sql_query=chat_response.optimized_query
                )
                return StopEvent(result=response)
            
            case "explain_sql":
                chat_response = self.sql_generator.generate(kwargs)
                response = schemas.SynthesisResult(
                    natural_language_response=chat_response.sql_query_explanation,
                    sql_query=""
                )
                return StopEvent(result=response)
            
            case "fix_sql":
                chat_response = self.sql_generator.generate(kwargs)
                response = schemas.SynthesisResult(
                    natural_language_response=chat_response.fix_explanation,
                    sql_query=chat_response.fixed_sql_query
                )
                return StopEvent(result=response)

            case _:
                raise ValueError(f"Unknown prompt_type: {self.prompt_type}")
    

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
    

async def starts_workflow(
        cnt_str: schemas.DatabaseConnection, 
        tables: List[str], 
        user_question: str, 
        have_obj_index: bool,
        prompt_type: str
        ) -> schemas.SynthesisResult:
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

    if prompt_type == "text_to_sql":
        prompt_strategy=TextToSQLPromptStrategy("postgresql")
    if prompt_type == "optimize_sql":
        prompt_strategy=OptimizesSQLQueryPromptStrategy("postgresql")
    if prompt_type == "explain_sql":
        prompt_strategy=ExplainSQLQueryPromptStrategy("postgresql")
    if prompt_type == "fix_sql":
        prompt_strategy=FixSQLQueryPromptStrategy("postgresql")

    sql_generator = OpenAISQLGenerator(
        llm=llm,
        prompt_strategy=prompt_strategy
    )

    print("sql_generator", sql_generator)

    txt_tosql_workflow = TextToSQLWorkflow(
        obj_retriever=obj_retriever,
        sql_run_query=sql_run_query,
        sql_generator=sql_generator,
        sql_database=sql_database,
        prompt_type=prompt_type
    )

    print("txt_tosql_workflow", txt_tosql_workflow)

    response = await txt_tosql_workflow.run(
        query=user_question,
        timeout=30
    )
    return response

async def starts_simple_workflow(
        user_question: str, 
        db_name: str, 
        prompt_type: str, 
        ) -> schemas.SynthesisResult:

    schema_retriever = SQLSchemaRetriever(
        db_name=db_name
    )

    print("schema_retriever", schema_retriever)

    

    llm = LLMFactory.create_llm("gpt-4o")
    
    if prompt_type == "text_to_sql":
        prompt_strategy=TextToSQLPromptStrategy("postgresql")
    if prompt_type == "optimize_sql":
        prompt_strategy=OptimizesSQLQueryPromptStrategy("postgresql")
    if prompt_type == "explain_sql":
        prompt_strategy=ExplainSQLQueryPromptStrategy("postgresql")
    if prompt_type == "fix_sql":
        prompt_strategy=FixSQLQueryPromptStrategy("postgresql")

    sql_generator = OpenAISQLGenerator(
        llm=llm,
        prompt_strategy=prompt_strategy
    )

    print("sql_generator", sql_generator)

    txt_tosql_workflow = SimpleTextToSQLWorkflow(
        schema_retriever=schema_retriever,
        sql_generator=sql_generator,
        prompt_type=prompt_type
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
