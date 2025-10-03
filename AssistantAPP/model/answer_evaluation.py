from pydantic import BaseModel, Field
from typing import Optional

class AnswerEvaluation(BaseModel):
    id: Optional[int] = None
    evaluate_queryquestion_id: int
    if_answer: int = Field(..., ge=0, le=1, description="Whether answer was provided (0 or 1)")
    technical_accuracy: Optional[float] = Field(None, ge=1.0, le=5.0, description="Likert scale 1-5")
    practical_utility: Optional[float] = Field(None, ge=1.0, le=5.0, description="Likert scale 1-5")
    trustworthiness: Optional[float] = Field(None, ge=1.0, le=5.0, description="Likert scale 1-5")
    comprehension_depth: Optional[float] = Field(None, ge=1.0, le=5.0, description="Likert scale 1-5")
    issues_found: Optional[str] = None
    suggestions_for_improvement: Optional[str] = None
    created_at: Optional[str] = None