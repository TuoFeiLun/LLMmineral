from pydantic import BaseModel
from typing import Optional


class QueryQuestion(BaseModel):
    conversation_id: int
    query: str
    # Prefer model_name; fall back to llmmodel_id if provided
    model_name: Optional[str] = "qwen2.5-7b"
    llmmodel_id: Optional[int] = None