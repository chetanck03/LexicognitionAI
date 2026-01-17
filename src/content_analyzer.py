"""Content analysis and RAG pipeline component."""
import logging
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from config import settings
from src.models import ParsedDocument, KnowledgeBase, TextChunk, Concept

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Analyzes document content and builds knowledge base with RAG."""
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_document(self, document: ParsedDocument) -> List[TextChunk]:
        """
        Split document into semantic chunks.
        
        Args:
            document: Parsed document to chunk
            
        Returns:
            List of text chunks with metadata
        """
        chunks = []
        
        # If we have sections, chunk each section separately
        if document.sections:
            for section in document.sections:
                section_chunks = self.text_splitter.split_text(section.content)
                for idx, chunk_text in enumerate(section_chunks):
                    chunks.append(TextChunk(
                        text=chunk_text,
                        section=section.heading,
                        page_number=section.page_number,
                        chunk_index=idx
                    ))
        else:
            # Chunk the entire document
            text_chunks = self.text_splitter.split_text(document.text)
            for idx, chunk_text in enumerate(text_chunks):
                chunks.append(TextChunk(
                    text=chunk_text,
                    section="Main Content",
                    page_number=0,
                    chunk_index=idx
                ))
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def build_vector_store(self, chunks: List[TextChunk], paper_id: str) -> FAISS:
        """
        Build FAISS vector store from chunks.
        
        Args:
            chunks: List of text chunks
            paper_id: Unique identifier for the paper
            
        Returns:
            FAISS vector store
        """
        # Convert chunks to LangChain documents
        documents = [
            Document(
                page_content=chunk.text,
                metadata={
                    'chunk_id': chunk.id,
                    'section': chunk.section,
                    'page_number': chunk.page_number,
                    'chunk_index': chunk.chunk_index,
                    'paper_id': paper_id
                }
            )
            for chunk in chunks
        ]
        
        # Create vector store
        vector_store = FAISS.from_documents(documents, self.embeddings)
        logger.info(f"Built vector store with {len(documents)} documents")
        
        return vector_store
    
    def extract_concepts(self, document: ParsedDocument, top_n: int = 20) -> List[Concept]:
        """
        Extract key concepts from the document.
        
        This is a simplified implementation. For production, you might want to use:
        - Named Entity Recognition (NER)
        - LLM-based concept extraction
        - Domain-specific terminology extraction
        
        Args:
            document: Parsed document
            top_n: Number of top concepts to extract
            
        Returns:
            List of extracted concepts
        """
        # Simple keyword extraction based on frequency and capitalization
        # This is a placeholder - in production, use more sophisticated methods
        
        concepts = []
        text = document.text
        
        # Extract capitalized phrases (likely to be technical terms)
        words = text.split()
        capitalized_terms = set()
        
        for i, word in enumerate(words):
            if word and word[0].isupper() and len(word) > 3:
                # Check for multi-word terms
                term = word
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    term = f"{word} {words[i + 1]}"
                capitalized_terms.add(term.strip('.,;:()[]{}'))
        
        # Create concept objects
        for term in list(capitalized_terms)[:top_n]:
            # Find context sentences containing the term
            sentences = text.split('.')
            context = [s.strip() for s in sentences if term in s][:3]
            
            concepts.append(Concept(
                term=term,
                definition=f"Key concept from the paper: {term}",
                context=context
            ))
        
        logger.info(f"Extracted {len(concepts)} concepts")
        return concepts
    
    def analyze(self, document: ParsedDocument, paper_id: str) -> KnowledgeBase:
        """
        Analyze document and build complete knowledge base.
        
        Args:
            document: Parsed document
            paper_id: Unique identifier for the paper
            
        Returns:
            KnowledgeBase with chunks, concepts, and vector store
        """
        logger.info(f"Analyzing document for paper {paper_id}")
        
        # Chunk the document
        chunks = self.chunk_document(document)
        
        # Build vector store
        vector_store = self.build_vector_store(chunks, paper_id)
        
        # Save vector store
        vector_store_path = settings.vector_store_path / paper_id
        vector_store_path.parent.mkdir(parents=True, exist_ok=True)
        vector_store.save_local(str(vector_store_path))
        
        # Extract concepts
        concepts = self.extract_concepts(document)
        
        return KnowledgeBase(
            paper_id=paper_id,
            chunks=chunks,
            concepts=concepts,
            vector_store_id=str(vector_store_path)
        )
    
    def query(self, vector_store_path: str, query: str, k: int = 5) -> List[Document]:
        """
        Query the vector store for relevant chunks.
        
        Args:
            vector_store_path: Path to saved vector store
            query: Query string
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        vector_store = FAISS.load_local(
            vector_store_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        results = vector_store.similarity_search(query, k=k)
        logger.info(f"Retrieved {len(results)} relevant chunks for query")
        
        return results
