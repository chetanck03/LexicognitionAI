"""Tests for data models."""
import pytest
from src.models import (
    Session, Question, QuestionType, SessionStatus,
    EvaluationResult, Correctness, AnswerRecord
)


class TestModels:
    """Test suite for data models."""
    
    def test_question_creation(self):
        """Test creating a question."""
        question = Question(
            text="Why does the paper propose this approach?",
            type=QuestionType.WHY,
            expected_concepts=["concept1", "concept2"],
            difficulty=3
        )
        
        assert question.text is not None
        assert question.type == QuestionType.WHY
        assert len(question.expected_concepts) == 2
    
    def test_evaluation_score_validation(self):
        """Test that evaluation scores are validated."""
        # Valid score
        eval_result = EvaluationResult(
            score=8,
            correctness=Correctness.CORRECT,
            feedback="Good answer"
        )
        assert eval_result.score == 8
        
        # Invalid score should raise error
        with pytest.raises(ValueError):
            EvaluationResult(
                score=11,  # Out of range
                correctness=Correctness.CORRECT,
                feedback="Test"
            )
    
    def test_session_properties(self):
        """Test session computed properties."""
        questions = [
            Question(
                text=f"Question {i}",
                type=QuestionType.WHY,
                expected_concepts=[]
            )
            for i in range(5)
        ]
        
        session = Session(
            user_id="test_user",
            paper_id="test_paper",
            questions=questions
        )
        
        # Test initial state
        assert session.status == SessionStatus.IN_PROGRESS
        assert session.current_question_index == 0
        assert session.current_question == questions[0]
        assert not session.is_complete
        
        # Add answers
        for i in range(5):
            session.answers.append(AnswerRecord(
                question_id=questions[i].id,
                answer="Test answer",
                score=8,
                feedback="Good",
                correctness=Correctness.CORRECT
            ))
        
        # Test completion
        assert session.is_complete
        assert session.total_score == 40
        assert session.average_score == 8.0
