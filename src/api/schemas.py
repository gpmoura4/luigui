from pydantic import BaseModel, Field
from llama_index.core.workflow import Event


class TableInfo(BaseModel):
    """Information regarding a structured table."""
    table_name: str = Field(
        ..., description="table name (must be underscores and NO spaces)"
    )


class TableRetrieveEvent(Event):
    """Result of running table retrieval."""
    table_context_str: str
    query: str

class SchemaRetrieveEvent(Event):
    """Result of running schema retrieval."""
    table_schema: str
    query: str


class TextToSQLEvent(Event):
    """Text-to-SQL event."""
    sql: str
    query: str

class WorkFlowResult(Event):
    sql_query: str
    response: str

class DatabaseConnection(BaseModel):
    """Database connection information."""
    host: str
    port: int
    username: str
    password: str
    name: str

    class Config:
        from_attributes = True
