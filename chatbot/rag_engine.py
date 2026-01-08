import os
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.schema import Document
import chromadb
from config.settings import (
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS,
    ASU_AI_API_TOKEN, ASU_AI_MODEL, ASU_AI_EMBEDDINGS_MODEL,
    ASU_AI_BASE_URL
)
from chatbot.utils import load_markdown_file, ensure_directory_exists

class RAGEngine:
    def __init__(self):
        # Use HuggingFace embeddings (local) since ASU AI embeddings endpoint has issues
        # Keep ASU AI for chat completions with GPT-5
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception as e:
            print(f"Warning: Could not load HuggingFace embeddings: {e}")
            print("Falling back to basic embeddings...")
            self.embeddings = None
            
        self.vectorstore = None
        self.qa_chain = None
        self.documents = []
        
    def load_documents(self, directory_path: str) -> None:
        """Load documents from a directory."""
        self.documents = []
        
        if not os.path.exists(directory_path):
            return
            
        # Load markdown files
        for file_path in os.listdir(directory_path):
            if file_path.endswith('.md'):
                full_path = os.path.join(directory_path, file_path)
                content = load_markdown_file(full_path)
                if content:
                    self.documents.append(Document(
                        page_content=content,
                        metadata={"source": file_path}
                    ))
        
        # Load text files
        for file_path in os.listdir(directory_path):
            if file_path.endswith('.txt'):
                full_path = os.path.join(directory_path, file_path)
                try:
                    with open(full_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.documents.append(Document(
                            page_content=content,
                            metadata={"source": file_path}
                        ))
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
    
    def create_vectorstore(self) -> None:
        """Create and populate the vector store."""
        if not self.documents:
            return
            
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        
        chunks = text_splitter.split_documents(self.documents)
        
        # Create vector store
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        
        # Create QA chain with ASU AI Platform
        if ASU_AI_API_TOKEN:
            llm = ChatOpenAI(
                model=ASU_AI_MODEL,
                temperature=0.7,
                openai_api_key=ASU_AI_API_TOKEN,
                base_url=ASU_AI_BASE_URL  # Use base_url instead of openai_api_base
            )
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": TOP_K_RESULTS}
                )
            )
    
    def query(self, question: str) -> str:
        """Query the RAG system with a question."""
        if not self.qa_chain:
            return "I don't have access to the knowledge base yet. Please ensure documents are loaded."
        
        try:
            response = self.qa_chain.run(question)
            return response
        except Exception as e:
            return f"Error querying the knowledge base: {str(e)}"
    
    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """Perform similarity search on the vector store."""
        if not self.vectorstore:
            return []
        
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
    
    def save_vectorstore(self, path: str) -> None:
        """Save the vector store to disk."""
        if self.vectorstore:
            ensure_directory_exists(os.path.dirname(path))
            self.vectorstore.save_local(path)
    
    def load_vectorstore(self, path: str) -> None:
        """Load the vector store from disk."""
        if os.path.exists(path):
            self.vectorstore = FAISS.load_local(path, self.embeddings)
            
            # Recreate QA chain with ASU AI Platform
            if ASU_AI_API_TOKEN:
                llm = ChatOpenAI(
                    model=ASU_AI_MODEL,
                    temperature=0.7,
                    openai_api_key=ASU_AI_API_TOKEN,
                    base_url=ASU_AI_BASE_URL  # Use base_url instead of openai_api_base
                )
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=self.vectorstore.as_retriever(
                        search_kwargs={"k": TOP_K_RESULTS}
                    )
                ) 