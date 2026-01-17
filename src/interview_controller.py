"""Interview flow controller."""
import logging
from typing import Optional
from datetime import datetime
from src.models import (
    Session, SessionStatus, Question, AnswerRecord,
    KnowledgeBase, EvaluationResult
)
from src.session_manager import SessionManager
from src.answer_evaluator import AnswerEvaluator

logger = logging.getLogger(__name__)


class InterviewController:
    """Controls the interactive examination flow."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.evaluator = AnswerEvaluator()
    
    def start_interview(
        self,
        user_id: str,
        paper_id: str,
        questions: list[Question]
    ) -> Session:
        """
        Start a new interview session.
        
        Args:
            user_id: User identifier
            paper_id: Paper identifier
            questions: List of questions for the interview
            
        Returns:
            Created session
        """
        logger.info(f"Starting interview for user {user_id} on paper {paper_id}")
        
        session = self.session_manager.create_session(user_id, paper_id, questions)
        
        return session
    
    def get_current_question(self, session_id: str) -> Optional[Question]:
        """
        Get the current question for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Current question or None if session complete
        """
        session = self.session_manager.get_session(session_id)
        
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        return session.current_question
    
    def submit_answer(
        self,
        session_id: str,
        answer: str,
        kb: KnowledgeBase
    ) -> EvaluationResult:
        """
        Submit an answer and get evaluation.
        
        Args:
            session_id: Session identifier
            answer: User's answer text
            kb: Knowledge base for the paper
            
        Returns:
            Evaluation result
            
        Raises:
            ValueError: If session not found or already complete
        """
        # Get session
        session = self.session_manager.get_session(session_id)
        
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        if session.status == SessionStatus.COMPLETED:
            raise ValueError("Session is already completed")
        
        # Get current question
        current_question = session.current_question
        
        if not current_question:
            raise ValueError("No current question available")
        
        logger.info(f"Evaluating answer for session {session_id}, question {session.current_question_index}")
        
        # Evaluate answer
        evaluation = self.evaluator.evaluate(current_question, answer, kb)
        
        # Record answer
        answer_record = AnswerRecord(
            question_id=current_question.id,
            answer=answer,
            score=evaluation.score,
            feedback=evaluation.feedback,
            correctness=evaluation.correctness,
            timestamp=datetime.utcnow()
        )
        
        session.answers.append(answer_record)
        
        # Move to next question
        session.current_question_index += 1
        
        # Check if interview is complete
        if session.is_complete:
            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.utcnow()
            logger.info(f"Interview completed for session {session_id}")
        
        # Save session
        self.session_manager.save_session(session)
        
        return evaluation
    
    def get_session_status(self, session_id: str) -> Optional[dict]:
        """
        Get current status of a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session status information
        """
        session = self.session_manager.get_session(session_id)
        
        if not session:
            return None
        
        return {
            'session_id': session.id,
            'status': session.status,
            'current_question_index': session.current_question_index,
            'total_questions': len(session.questions),
            'questions_remaining': len(session.questions) - len(session.answers),
            'current_question': session.current_question.model_dump() if session.current_question else None,
            'answers': [a.model_dump(mode='json') for a in session.answers],
            'total_score': session.total_score,
            'average_score': session.average_score,
            'started_at': session.started_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None
        }
    
    def pause_session(self, session_id: str) -> bool:
        """
        Pause an active session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if paused successfully
        """
        session = self.session_manager.get_session(session_id)
        
        if not session or session.status != SessionStatus.IN_PROGRESS:
            return False
        
        session.status = SessionStatus.PAUSED
        self.session_manager.save_session(session)
        
        logger.info(f"Session paused: {session_id}")
        return True
    
    def resume_session(self, session_id: str) -> bool:
        """
        Resume a paused session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if resumed successfully
        """
        session = self.session_manager.get_session(session_id)
        
        if not session or session.status != SessionStatus.PAUSED:
            return False
        
        session.status = SessionStatus.IN_PROGRESS
        self.session_manager.save_session(session)
        
        logger.info(f"Session resumed: {session_id}")
        return True
