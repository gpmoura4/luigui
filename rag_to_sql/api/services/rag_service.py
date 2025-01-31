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


class SQLTableRetriever():
    def __init__(self, engine, table_infos):
        sql_database = SQLDatabase(engine)

        table_node_mapping = SQLTableNodeMapping(sql_database)
        table_schema_objs = [
            SQLTableSchema(table_name=t.table_name, context_str=t.table_summary)
            for t in table_infos
        ]  # add a SQLTableSchema for each table

        self.obj_index = ObjectIndex.from_objects(
            table_schema_objs,
            table_node_mapping,
            VectorStoreIndex,
        )

    def retrieve(self, top_k: int = 3):
        return self.obj_index.as_retriever(similarity_top_k=top_k)


class SQLRetriever():
    def __init__(self, sql_database):
        self.sql_retriever = SQLRetriever(sql_database)


class TextToSQLWorkflow(Workflow):
    """Text-to-SQL Workflow that does query-time table retrieval."""

    def __init__(
        self,
        obj_retriever: SQLTableRetriever,
        text2sql_prompt,
        sql_retriever,
        response_synthesis_prompt,
        llm,
        *args,
        **kwargs
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self.obj_retriever = obj_retriever
        self.text2sql_prompt = text2sql_prompt
        self.sql_retriever = sql_retriever
        self.response_synthesis_prompt = response_synthesis_prompt
        self.llm = llm
