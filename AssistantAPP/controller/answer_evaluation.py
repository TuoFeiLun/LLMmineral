"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/10/03 22:31  
@ModifiedBy  : Yujia LI
@Description : Answer evaluation API endpoints for evaluating LLM responses
@Version     : 0.0.1
@License     : None
"""

from fastapi import APIRouter, HTTPException
from model.answer_evaluation import AnswerEvaluation
from database import answer_evaluationdb

answer_evaluation_router = APIRouter()


@answer_evaluation_router.post("/answer_evaluation", status_code=201)
async def create_answer_evaluation(answer_evaluation: AnswerEvaluation):
    """
    Create a new answer evaluation for a query question.
    Each question can only have ONE evaluation.
    
    Args:
        answer_evaluation: AnswerEvaluation model with evaluation metrics
        
    Returns:
        Dict with created evaluation ID
    """
    try:
        # Check if evaluation already exists for this question
        existing = answer_evaluationdb.get_answer_evaluation_by_question_id(
            answer_evaluation.evaluate_queryquestion_id
        )
        if existing:
            raise HTTPException(
                status_code=409, 
                detail=f"An evaluation already exists for question ID {answer_evaluation.evaluate_queryquestion_id}. Use PATCH to update it."
            )
        
        evaluation_id = answer_evaluationdb.create_answer_evaluation(answer_evaluation)
        return {
            "message": "Answer evaluation created successfully",
            "evaluation_id": evaluation_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create evaluation: {str(e)}")


@answer_evaluation_router.patch("/answer_evaluation/{evaluation_id}")
async def update_answer_evaluation(evaluation_id: int, answer_evaluation: AnswerEvaluation):
    """
    Update an existing answer evaluation.
    
    Args:
        evaluation_id: ID of the evaluation to update
        answer_evaluation: Updated evaluation data
        
    Returns:
        Success message
    """
    try:
        rows_affected = answer_evaluationdb.update_answer_evaluation(evaluation_id, answer_evaluation)
        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="Answer evaluation not found")
        return {"message": "Answer evaluation updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update evaluation: {str(e)}")


@answer_evaluation_router.get("/answer_evaluation/{evaluation_id}")
async def get_answer_evaluation(evaluation_id: int):
    """
    Get answer evaluation by evaluation ID.
    
    Args:
        evaluation_id: ID of the evaluation
        
    Returns:
        Answer evaluation data
    """
    try:
        evaluation = answer_evaluationdb.get_answer_evaluation_by_id(evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Answer evaluation not found")
        return evaluation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation: {str(e)}")


@answer_evaluation_router.get("/answer_evaluation/question/{question_id}")
async def get_answer_evaluation_by_question(question_id: int):
    """
    Get answer evaluation by query question ID.
    
    Args:
        question_id: ID of the query question
        
    Returns:
        Answer evaluation data
    """
    try:
        evaluation = answer_evaluationdb.get_answer_evaluation_by_question_id(question_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Answer evaluation not found for this question")
        return evaluation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation: {str(e)}")


@answer_evaluation_router.get("/answer_evaluations")
async def get_all_answer_evaluations():
    """
    Get all answer evaluations.
    
    Returns:
        List of all answer evaluations
    """
    try:
        evaluations = answer_evaluationdb.get_all_answer_evaluations()
        return {
            "evaluations": evaluations,
            "count": len(evaluations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evaluations: {str(e)}")


@answer_evaluation_router.delete("/answer_evaluation/{evaluation_id}")
async def delete_answer_evaluation(evaluation_id: int):
    """
    Delete an answer evaluation.
    
    Args:
        evaluation_id: ID of the evaluation to delete
        
    Returns:
        Success message
    """
    try:
        rows_affected = answer_evaluationdb.delete_answer_evaluation(evaluation_id)
        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="Answer evaluation not found")
        return {"message": "Answer evaluation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete evaluation: {str(e)}")

