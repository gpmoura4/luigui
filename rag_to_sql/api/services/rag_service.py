from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Context,
    Event,
)


class TextToSQLWorkflow1(Workflow):
    """Text-to-SQL Workflow that does query-time table retrieval."""

    def __init__(
        self,
        obj_retriever,
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