import sqlite3
from database.creatSQL import get_connection
from model.answer_evaluation import AnswerEvaluation


def create_answer_evaluation(answer_evaluation: AnswerEvaluation):
    """Create a new answer evaluation record."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO answer_evaluate (
                evaluate_queryquestion_id, if_answer, technical_accuracy, 
                practical_utility, trustworthiness, comprehension_depth,
                issues_found, suggestions_for_improvement
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                answer_evaluation.evaluate_queryquestion_id,
                answer_evaluation.if_answer,
                answer_evaluation.technical_accuracy,
                answer_evaluation.practical_utility,
                answer_evaluation.trustworthiness,
                answer_evaluation.comprehension_depth,
                answer_evaluation.issues_found,
                answer_evaluation.suggestions_for_improvement
            )
        )
        conn.commit()
        return cur.lastrowid


def get_answer_evaluation_by_id(evaluation_id: int):
    """Get answer evaluation by its ID."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM answer_evaluate WHERE id = ?", (evaluation_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_answer_evaluation_by_question_id(question_id: int):
    """Get answer evaluation by question ID."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM answer_evaluate WHERE evaluate_queryquestion_id = ?",
            (question_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def update_answer_evaluation(evaluation_id: int, answer_evaluation: AnswerEvaluation):
    """Update an existing answer evaluation record."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE answer_evaluate SET 
                evaluate_queryquestion_id = ?,
                if_answer = ?,
                technical_accuracy = ?,
                practical_utility = ?,
                trustworthiness = ?,
                comprehension_depth = ?,
                issues_found = ?,
                suggestions_for_improvement = ?
            WHERE id = ?
            """,
            (
                answer_evaluation.evaluate_queryquestion_id,
                answer_evaluation.if_answer,
                answer_evaluation.technical_accuracy,
                answer_evaluation.practical_utility,
                answer_evaluation.trustworthiness,
                answer_evaluation.comprehension_depth,
                answer_evaluation.issues_found,
                answer_evaluation.suggestions_for_improvement,
                evaluation_id
            )
        )
        conn.commit()
        return cur.rowcount


def delete_answer_evaluation(evaluation_id: int):
    """Delete an answer evaluation by its ID."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM answer_evaluate WHERE id = ?", (evaluation_id,))
        conn.commit()
        return cur.rowcount


def get_all_answer_evaluations():
    """Get all answer evaluations."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM answer_evaluate ORDER BY created_at DESC")
        rows = cur.fetchall()
        return [dict(row) for row in rows]