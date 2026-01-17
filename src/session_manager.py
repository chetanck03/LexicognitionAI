"""Session management and persistence."""
import logging
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as DBSession
from config import settings
from src.models import Session, SessionStatus, SessionSummary, AnswerRecord, Question, Correctness

logger = logging.getLogger(__name__)

Base = declarative_base()


class SessionDB(Base):
    """Database model for sessions."""
    __tablename__ = 'sessions'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    paper_id = Column(String, nullable=False)
    questions_json = Column(Text, nullable=False)
    answers_json = Column(Text, nullable=False)
    current_question_index = Column(Integer, default=0)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.IN_PROGRESS)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class SessionManager:
    """Manages examination sessions with persistence."""
    
    def __init__(self):
        # Ensure database directory exists
        settings.ensure_directories()
        
        # Create database engine
        db_url = f"sqlite:///{settings.session_db_path}"
        self.engine = create_engine(db_url, echo=False)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        logger.info(f"Session manager initialized with database: {settings.session_db_path}")
    
    def _serialize_questions(self, questions: List[Question]) -> str:
        """Serialize questions to JSON."""
        return json.dumps([q.model_dump() for q in questions])
    
    def _deserialize_questions(self, questions_json: str) -> List[Question]:
        """Deserialize questions from JSON."""
        data = json.loads(questions_json)
        return [Question(**q) for q in data]
    
    def _serialize_answers(self, answers: List[AnswerRecord]) -> str:
        """Serialize answers to JSON."""
        return json.dumps([a.model_dump(mode='json') for a in answers])
    
    def _deserialize_answers(self, answers_json: str) -> List[AnswerRecord]:
        """Deserialize answers from JSON."""
        if not answers_json:
            return []
        data = json.loads(answers_json)
        return [AnswerRecord(**a) for a in data]
    
    def create_session(self, user_id: str, paper_id: str, questions: List[Question]) -> Session:
        """
        Create a new examination session.
        
        Args:
            user_id: User identifier
            paper_id: Paper identifier
            questions: List of questions for the session
            
        Returns:
            Created session
        """
        session = Session(
            user_id=user_id,
            paper_id=paper_id,
            questions=questions,
            answers=[],
            current_question_index=0,
            status=SessionStatus.IN_PROGRESS
        )
        
        # Save to database
        db_session = self.SessionLocal()
        try:
            db_record = SessionDB(
                id=session.id,
                user_id=session.user_id,
                paper_id=session.paper_id,
                questions_json=self._serialize_questions(session.questions),
                answers_json=self._serialize_answers(session.answers),
                current_question_index=session.current_question_index,
                status=session.status,
                started_at=session.started_at
            )
            db_session.add(db_record)
            db_session.commit()
            logger.info(f"Created session: {session.id}")
        finally:
            db_session.close()
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session if found, None otherwise
        """
        db_session = self.SessionLocal()
        try:
            db_record = db_session.query(SessionDB).filter(SessionDB.id == session_id).first()
            
            if not db_record:
                return None
            
            session = Session(
                id=db_record.id,
                user_id=db_record.user_id,
                paper_id=db_record.paper_id,
                questions=self._deserialize_questions(db_record.questions_json),
                answers=self._deserialize_answers(db_record.answers_json),
                current_question_index=db_record.current_question_index,
                status=db_record.status,
                started_at=db_record.started_at,
                completed_at=db_record.completed_at
            )
            
            return session
        finally:
            db_session.close()
    
    def save_session(self, session: Session) -> None:
        """
        Save session state to database.
        
        Args:
            session: Session to save
        """
        db_session = self.SessionLocal()
        try:
            db_record = db_session.query(SessionDB).filter(SessionDB.id == session.id).first()
            
            if db_record:
                db_record.answers_json = self._serialize_answers(session.answers)
                db_record.current_question_index = session.current_question_index
                db_record.status = session.status
                db_record.completed_at = session.completed_at
                db_session.commit()
                logger.info(f"Updated session: {session.id}")
            else:
                logger.error(f"Session not found: {session.id}")
        finally:
            db_session.close()
    
    def list_user_sessions(self, user_id: str) -> List[SessionSummary]:
        """
        List all sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session summaries
        """
        db_session = self.SessionLocal()
        try:
            records = db_session.query(SessionDB).filter(
                SessionDB.user_id == user_id,
                SessionDB.status == SessionStatus.COMPLETED
            ).order_by(SessionDB.completed_at.desc()).all()
            
            summaries = []
            for record in records:
                answers = self._deserialize_answers(record.answers_json)
                
                # Calculate statistics
                total_score = sum(a.score for a in answers)
                avg_score = total_score / len(answers) if answers else 0
                
                num_correct = sum(1 for a in answers if a.correctness == Correctness.CORRECT)
                num_partial = sum(1 for a in answers if a.correctness == Correctness.PARTIALLY_CORRECT)
                num_incorrect = sum(1 for a in answers if a.correctness == Correctness.INCORRECT)
                
                summaries.append(SessionSummary(
                    session_id=record.id,
                    paper_title=f"Paper {record.paper_id}",  # You might want to fetch actual title
                    total_score=total_score,
                    average_score=avg_score,
                    num_questions=len(answers),
                    num_correct=num_correct,
                    num_partially_correct=num_partial,
                    num_incorrect=num_incorrect,
                    completed_at=record.completed_at
                ))
            
            return summaries
        finally:
            db_session.close()
