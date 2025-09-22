from pydantic import BaseModel
from typing import Optional
class QueryQuestion(BaseModel):
    conversation_id: int
    query: str
    model_name: Optional[int] = 1