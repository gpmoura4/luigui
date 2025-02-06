from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Context,
    Event,
)

from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
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

import os
import openai

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv["OPENAI_API_KEY"]


class PromptFactory:
    @staticmethod
    def create_text2sql_prompt(engine):
        return DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
            dialect=engine.dialect.name
        )

    @staticmethod
    def create_response_synthesis_prompt():
        return PromptTemplate(
            "Given an input question, synthesize a response from the query results.\n"
            "Query: {query_str}\nSQL: {sql_query}\nSQL Response: {context_str}\nResponse: "
        )

#OPEN_AI CLASS
class OpenAISQLGenerator():
    def __init__(self, llm):
        self.llm = llm
        # self.prompt = text2sql_prompt
    
    def generate(self, context: str, query: str, prompt: str) -> str:
        fmt_messages = prompt.format_messages(
            query_str=query, schema=context
        )
        return self.llm.chat(fmt_messages)

class LLMFactory:
    @staticmethod
    def create_llm(model: str):
        return OpenAI(model=model)


class SQLTableRetriever():
    def __init__(self, engine, table_infos):
        sql_database = SQLDatabase(engine)

        # Criando um nó pra cada tabela do Banco
        table_node_mapping = SQLTableNodeMapping(sql_database)
        # add a SQLTableSchema for each table com nome e contexto
        table_schema_objs = [
            SQLTableSchema(table_name=t.table_name, context_str=t.table_summary)
            for t in table_infos
        ]  
        # Base de dados vetoriais
        self.obj_index = ObjectIndex.from_objects(
            table_schema_objs,
            table_node_mapping,
            VectorStoreIndex,
        )
        self.obj_retriever = self.obj_index.as_retriever(similarity_top_k=3)

    # def retrieve(self, top_k: int = 3):
    #     return self.obj_index.as_retriever(similarity_top_k=top_k)


# Class que executa as querys no banco
class SQLRunQuery():
    def __init__(self, sql_database):
        self.sql_executor = SQLRetriever(sql_database)


class TableRetrieveEvent(Event):
    """Result of running table retrieval."""

    table_context_str: str
    query: str

class TextToSQLEvent(Event):
    """Text-to-SQL event."""

    sql: str
    query: str

class TextToSQLWorkflow(Workflow):
    """Text-to-SQL Workflow that does query-time table retrieval."""

    def __init__(
        self,
        obj_retriever: SQLTableRetriever,
        text2sql_prompt,
        sql_executor: SQLRunQuery,
        response_synthesis_prompt,
        sql_generator: OpenAISQLGenerator,
        *args,
        **kwargs
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self.obj_retriever = obj_retriever
        self.text2sql_prompt = text2sql_prompt
        self.sql_executor = sql_executor
        self.response_synthesis_prompt = response_synthesis_prompt
        self.sql_generator = sql_generator
    
    @step
    def retrieve_tables(
        self, ctx: Context, ev: StartEvent
    ) -> TableRetrieveEvent:
        """Retrieve tables."""
        table_schema_objs = self.obj_retriever.retrieve(ev.query)
        table_context_str = get_table_context_str(table_schema_objs)
        print("###",table_context_str, "###")
        return TableRetrieveEvent(
            table_context_str=table_context_str, query=ev.query
        )
    
    @step
    def generate_sql(
        self, ctx: Context, ev: TableRetrieveEvent
    ) -> TextToSQLEvent:
        """Generate SQL statement."""
        chat_response = self.sql_generator.generate(ctx, ev.query, PromptFactory.create_text2sql_prompt())
        sql = parse_response_to_sql(chat_response)
        return TextToSQLEvent(sql=sql, query=ev.query)
    
    @step
    def generate_response(self, ctx: Context, ev: TextToSQLEvent) -> StopEvent:
        """Run SQL retrieval and generate response."""
        #Executar a query no banco
        retrieved_rows = self.sql_retriever.retrieve(ev.sql)
        fmt_messages = PromptFactory.create_response_synthesis_prompt(
            sql_query=ev.sql,
            context_str=str(retrieved_rows),
            query_str=ev.query,
        )
        chat_response = llm.chat(fmt_messages)
        return StopEvent(result=chat_response)