"""Answer evaluation component using LLM."""
import logging
from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from config import settings
from src.models import Question, EvaluationResult, Correctness, KnowledgeBase
from src.content_analyzer import ContentAnalyzer

logger = logging.getLogger(__name__)


class AnswerEvaluator:
    """Evaluates user answers against paper content."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.3,  # Lower temperature for more consistent evaluation
            max_tokens=settings.llm_max_tokens,
            openai_api_key=settings.openai_api_key
        )
        self.content_analyzer = ContentAnalyzer()
        self.min_score = settings.min_score
        self.max_score = settings.max_score
    
    def _create_evaluation_prompt(
        self,
        question: Question,
        answer: str,
        paper_context: str,
        expected_concepts: List[str]
    ) -> ChatPromptTemplate:
        """
        Create prompt for answer evaluation.
        
        Args:
            question: The question being answered
            answer: User's answer
            paper_context: Relevant context from the paper
            expected_concepts: Concepts that should be in the answer
            
        Returns:
            ChatPromptTemplate for evaluation
        """
        template = """You are evaluating a student's answer to a viva voce question about a research paper.

Question: {question}

Student Answer: {answer}

Paper Context (Ground Truth):
{paper_context}

Expected Key Concepts: {expected_concepts}

Evaluate the answer based on:
1. Factual Accuracy (40%): Does it contradict the paper? Are there factual errors?
2. Completeness (30%): Does it cover the key concepts?
3. Depth of Understanding (30%): Is it superficial or demonstrates deep understanding?

Provide your evaluation in JSON format with these fields:
- score: Integer from {min_score} to {max_score}
- correctness: One of "correct", "partially_correct", or "incorrect"
- feedback: Detailed constructive feedback (2-3 sentences)
- factual_errors: List of specific factual errors (empty list if none)
- missing_concepts: List of key concepts not mentioned (empty list if none)

Be strict but fair. An answer is "correct" only if it's factually accurate and covers most key concepts.
"""
        
        return ChatPromptTemplate.from_template(template)
    
    def _parse_evaluation_response(self, response: str) -> dict:
        """
        Parse LLM evaluation response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Dictionary with evaluation data
        """
        import json
        import re
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                eval_data = json.loads(json_match.group())
            else:
                eval_data = json.loads(response)
            
            # Validate and normalize
            eval_data['score'] = max(self.min_score, min(self.max_score, int(eval_data.get('score', 5))))
            eval_data['correctness'] = eval_data.get('correctness', 'partially_correct').lower()
            eval_data['feedback'] = eval_data.get('feedback', 'No feedback provided')
            eval_data['factual_errors'] = eval_data.get('factual_errors', [])
            eval_data['missing_concepts'] = eval_data.get('missing_concepts', [])
            
            return eval_data
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse evaluation response: {e}")
            logger.debug(f"Response was: {response}")
            
            # Return default evaluation
            return {
                'score': 5,
                'correctness': 'partially_correct',
                'feedback': 'Unable to evaluate answer properly. Please try again.',
                'factual_errors': [],
                'missing_concepts': []
            }
    
    def evaluate(
        self,
        question: Question,
        answer: str,
        kb: KnowledgeBase
    ) -> EvaluationResult:
        """
        Evaluate a user's answer.
        
        Args:
            question: The question being answered
            answer: User's answer text
            kb: Knowledge base for the paper
            
        Returns:
            EvaluationResult with score and feedback
        """
        logger.info(f"Evaluating answer for question: {question.id}")
        
        # Retrieve relevant context from paper
        relevant_chunks = self.content_analyzer.query(
            kb.vector_store_id,
            question.text + " " + answer,
            k=5
        )
        
        paper_context = "\n\n".join([doc.page_content for doc in relevant_chunks])
        
        # Create evaluation prompt
        prompt = self._create_evaluation_prompt(
            question.text,
            answer,
            paper_context,
            question.expected_concepts
        )
        
        messages = prompt.format_messages(
            question=question.text,
            answer=answer,
            paper_context=paper_context,
            expected_concepts=", ".join(question.expected_concepts),
            min_score=self.min_score,
            max_score=self.max_score
        )
        
        # Get evaluation from LLM
        response = self.llm.invoke(messages)
        
        # Parse response
        eval_data = self._parse_evaluation_response(response.content)
        
        # Create evaluation result
        result = EvaluationResult(
            score=eval_data['score'],
            correctness=Correctness(eval_data['correctness']),
            feedback=eval_data['feedback'],
            factual_errors=eval_data['factual_errors'],
            missing_concepts=eval_data['missing_concepts']
        )
        
        logger.info(
            f"Evaluation complete: score={result.score}, "
            f"correctness={result.correctness}"
        )
        
        return result
