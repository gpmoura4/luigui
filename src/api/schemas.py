from pydantic import BaseModel, Field
from typing import Optional
from llama_index.core.workflow import Event


class TableInfo(BaseModel):
    """Information regarding a structured table."""
    table_name: str 
    table_context: Optional[str] = None


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
    sql_query: str
    natural_language_query: str


class SynthesisResult(Event):
    sql_query: str
    natural_language_response: str


class OptimizeResult(Event):
    """Result of running optimization."""
    optimized_query: str
    optimization_explanation: str


class ExplainSQLResult(Event):
    """Result of running optimization."""
    sql_query_explanation: str


class FixSQLResult(Event):
    """Result of fixing a query."""
    fixed_sql_query: str
    fix_explanation: str


class DatabaseConnection(BaseModel):
    """Database connection information."""
    host: str
    port: int
    username: str
    password: str
    name: str


    class Config:
        from_attributes = True


class SchemaSummary(BaseModel):
    """Schema Summary"""
    schema_summary: str
