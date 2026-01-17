"""Data models for the AI Viva Examiner system."""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4


class QuestionType(str, Enum):
    """Types of questions that can be generated."""
    WHY = "why"
    HOW = "how"
    EXPLAIN = "explain"
    COMPARE = "compare"
    APPLY = "apply"


class Correctness(str, Enum):
    """Answer correctness classification."""
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"


class SessionStatus(str, Enum):
    """Session lifecycle states."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


class Section(BaseModel):
    """A section of a parsed document."""
    heading: str
    content: str
    page_number: int


class ParsedDocument(BaseModel):
    """Structured representation of a parsed PDF."""
    text: str
    metadata: dict
    sections: List[Section] = []


class TextChunk(BaseModel):
    """A chunk of text with embedding and metadata."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    section: str
    page_number: int
    chunk_index: int


class Concept(BaseModel):
    """An extracted concept from the paper."""
    term: str
    definition: str
    context: List[str] = []


class KnowledgeBase(BaseModel):
    """Knowledge base built from a research paper."""
    paper_id: str
    chunks: List[TextChunk]
    concepts: List[Concept]
    vector_store_id: Optional[str] = None


class Question(BaseModel):
    """A generated question for the viva examination."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    type: QuestionType
    expected_concepts: List[str] = []
    relevant_chunks: List[str] = []
    difficulty: int = Field(ge=1, le=5, default=3)


class EvaluationResult(BaseModel):
    """Result of answer evaluation."""
    score: int = Field(ge=1, le=10)
    correctness: Correctness
    feedback: str
    factual_errors: List[str] = []
    missing_concepts: List[str] = []
    
    @validator('score')
    def validate_score_range(cls, v):
        """Ensure score is within valid range."""
        if not 1 <= v <= 10:
            raise ValueError('Score must be between 1 and 10')
        return v


class AnswerRecord(BaseModel):
    """Record of a user's answer to a question."""
    question_id: str
    answer: str
    score: int
    feedback: str
    correctness: Correctness
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    """An examination session."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    paper_id: str
    questions: List[Question]
    answers: List[AnswerRecord] = []
    current_question_index: int = 0
    status: SessionStatus = SessionStatus.IN_PROGRESS
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    @property
    def total_score(self) -> int:
        """Calculate total score from all answers."""
        return sum(answer.score for answer in self.answers)
    
    @property
    def average_score(self) -> float:
        """Calculate average score."""
        if not self.answers:
            return 0.0
        return self.total_score / len(self.answers)
    
    @property
    def current_question(self) -> Optional[Question]:
        """Get the current question."""
        if 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    @property
    def is_complete(self) -> bool:
        """Check if all questions have been answered."""
        return len(self.answers) >= len(self.questions)


class SessionSummary(BaseModel):
    """Summary of a completed session."""
    session_id: str
    paper_title: str
    total_score: int
    average_score: float
    num_questions: int
    num_correct: int
    num_partially_correct: int
    num_incorrect: int
    completed_at: datetime


class Paper(BaseModel):
    """Representation of an uploaded research paper."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    authors: List[str] = []
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: str
    page_count: int
