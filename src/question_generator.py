"""Question generation component using LLM."""
import logging
from typing import List
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from config import settings
from src.models import KnowledgeBase, Question, QuestionType
from src.content_analyzer import ContentAnalyzer

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generates conceptual questions from research papers."""
    
    def __init__(self):
        # Initialize LLM based on provider
        if settings.llm_provider == "groq":
            self.llm = ChatGroq(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                groq_api_key=settings.groq_api_key
            )
            logger.info(f"Using Groq API with model: {settings.llm_model}")
        else:
            self.llm = ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                openai_api_key=settings.openai_api_key
            )
            logger.info(f"Using OpenAI API with model: {settings.llm_model}")
        
        self.content_analyzer = ContentAnalyzer()
        self.num_questions = settings.num_questions
    
    def _create_generation_prompt(self, paper_context: str, concepts: List[str]) -> ChatPromptTemplate:
        """
        Create prompt for question generation.
        
        Args:
            paper_context: Relevant context from the paper
            concepts: Key concepts extracted from the paper
            
        Returns:
            ChatPromptTemplate for question generation
        """
        template = """You are an expert examiner conducting a viva voce examination on a research paper.

Paper Context:
{paper_context}

Key Concepts:
{concepts}

Generate exactly {num_questions} conceptual questions that:
1. Test deep understanding (prefer "Why" and "How" questions)
2. Are specific to this paper's content and methodology
3. Cannot be answered without reading and understanding the paper
4. Cover different aspects of the paper (methodology, results, implications, etc.)
5. Range from moderate to challenging difficulty
6. Avoid generic questions like "What is the title?" or "Who are the authors?"

For each question, provide:
- The question text
- The question type (why/how/explain/compare/apply)
- Expected key concepts that should appear in a good answer
- Difficulty level (1-5)

Format your response as a JSON array of objects with fields: text, type, expected_concepts, difficulty.
"""
        
        return ChatPromptTemplate.from_template(template)
    
    def _parse_llm_response(self, response: str) -> List[dict]:
        """
        Parse LLM response into structured question data.
        
        Args:
            response: Raw LLM response
            
        Returns:
            List of question dictionaries
        """
        import json
        import re
        
        # Try to extract JSON from response
        try:
            # Look for JSON array in the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                return questions_data
            else:
                # Try parsing the entire response
                questions_data = json.loads(response)
                return questions_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError("LLM did not return valid JSON")
    
    def _validate_questions(self, questions: List[Question], paper_text: str) -> List[Question]:
        """
        Validate that questions are paper-specific and meet requirements.
        
        Args:
            questions: Generated questions
            paper_text: Full paper text for validation
            
        Returns:
            Validated questions
        """
        validated = []
        paper_lower = paper_text.lower()
        
        for q in questions:
            # Check if question contains paper-specific content
            # (at least one expected concept should appear in the paper)
            is_specific = any(
                concept.lower() in paper_lower 
                for concept in q.expected_concepts
            )
            
            # Check for generic patterns
            generic_patterns = [
                'what is the title',
                'who are the authors',
                'when was',
                'where was published'
            ]
            is_generic = any(pattern in q.text.lower() for pattern in generic_patterns)
            
            if is_specific and not is_generic:
                validated.append(q)
            else:
                logger.warning(f"Filtered out question: {q.text}")
        
        return validated
    
    def generate(self, kb: KnowledgeBase, paper_text: str) -> List[Question]:
        """
        Generate questions from knowledge base.
        
        Args:
            kb: Knowledge base built from the paper
            paper_text: Full text of the paper
            
        Returns:
            List of exactly num_questions questions
            
        Raises:
            ValueError: If unable to generate required number of questions
        """
        logger.info(f"Generating {self.num_questions} questions")
        
        # Get relevant context from vector store
        # Query with general prompts to get diverse content
        queries = [
            "main methodology and approach",
            "key results and findings",
            "implications and contributions",
            "limitations and future work"
        ]
        
        relevant_chunks = []
        for query in queries:
            chunks = self.content_analyzer.query(kb.vector_store_id, query, k=3)
            relevant_chunks.extend(chunks)
        
        # Combine context
        paper_context = "\n\n".join([doc.page_content for doc in relevant_chunks[:10]])
        concepts = [c.term for c in kb.concepts[:15]]
        
        # Generate questions
        prompt = self._create_generation_prompt(paper_context, concepts)
        
        messages = prompt.format_messages(
            paper_context=paper_context,
            concepts=", ".join(concepts),
            num_questions=self.num_questions
        )
        
        response = self.llm.invoke(messages)
        
        # Parse response
        questions_data = self._parse_llm_response(response.content)
        
        # Convert to Question objects
        questions = []
        for q_data in questions_data:
            try:
                question = Question(
                    text=q_data['text'],
                    type=QuestionType(q_data.get('type', 'explain').lower()),
                    expected_concepts=q_data.get('expected_concepts', []),
                    difficulty=q_data.get('difficulty', 3)
                )
                questions.append(question)
            except Exception as e:
                logger.warning(f"Failed to parse question: {e}")
                continue
        
        # Validate questions
        validated_questions = self._validate_questions(questions, paper_text)
        
        # Ensure we have exactly the required number
        if len(validated_questions) < self.num_questions:
            logger.warning(
                f"Only generated {len(validated_questions)} valid questions, "
                f"expected {self.num_questions}"
            )
            # In production, you might want to retry generation here
        
        # Return exactly num_questions (or all if less)
        return validated_questions[:self.num_questions]
