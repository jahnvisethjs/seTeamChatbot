import os
import requests
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from config.settings import (
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS,
    ASU_AI_API_TOKEN, ASU_AI_MODEL, ASU_AI_EMBEDDINGS_MODEL,
    ASU_AI_BASE_URL
)
from chatbot.utils import load_markdown_file, ensure_directory_exists

class ASUAILM(Runnable):
    """Custom LLM wrapper for ASU AI Platform API with correct header format."""
    
    def __init__(self, api_token: str, base_url: str, model: str, temperature: float = 0.7):
        self.api_token = api_token
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.api_url = f"{base_url}/query"
    
    def invoke(self, input_data: Any, config: Dict = None) -> str:
        """Invoke the LLM with the given input."""
        # Extract the query string from different input types
        if isinstance(input_data, str):
            query = input_data
        elif isinstance(input_data, list):
            # Extract the last user message from message list
            for msg in reversed(input_data):
                if isinstance(msg, HumanMessage):
                    query = msg.content
                    break
                elif isinstance(msg, dict) and msg.get("role") == "user":
                    query = msg["content"]
                    break
            else:
                query = str(input_data)
        elif isinstance(input_data, dict) and "messages" in input_data:
            # Extract last user message
            messages = input_data["messages"]
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    query = msg["content"]
                    break
            else:
                query = str(input_data)
        else:
            # Assume it's a prompt value from ChatPromptTemplate
            query = str(input_data)
        
        # Make API request with correct header format
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # ASU AI Platform payload format
        payload = {
            "query": query,
            "model_provider": "openai",
            "model_name": self.model,
            "model_params": {
                "temperature": self.temperature
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract content from ASU AI Platform response
            # The response format is: {"response": "text content"}
            if "response" in result:
                return result["response"]
            elif "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "message" in result:
                return result["message"]["content"]
            else:
                return str(result)
                
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. The AI service may be slow or unavailable.")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"ASU AI API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Error calling ASU AI API: {str(e)}")

class RAGEngine:
    def __init__(self):
        # Lazy load embeddings - don't load until needed
        self._embeddings = None
        self.vectorstore = None
        self.llm = None
        self.rag_chain = None
        self.documents = []
    
    @property
    def embeddings(self):
        """Lazy load embeddings only when needed."""
        if self._embeddings is None:
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
                self._embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
            except Exception as e:
                self._embeddings = None
        return self._embeddings
        
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
        
        # Create LLM and RAG chain with ASU AI Platform
        if ASU_AI_API_TOKEN:
            self.llm = ASUAILM(
                api_token=ASU_AI_API_TOKEN,
                base_url=ASU_AI_BASE_URL,
                model=ASU_AI_MODEL,
                temperature=0.7
            )
            
            # Create RAG prompt template
            template = """Answer the question based only on the following context:

{context}

Question: {question}

Answer:"""
            prompt = ChatPromptTemplate.from_template(template)
            
            # Create RAG chain using LCEL (LangChain Expression Language)
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": TOP_K_RESULTS})
            
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            self.rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
    
    def query(self, question: str) -> str:
        """Query the RAG system with a question."""
        if not self.rag_chain:
            return "I don't have access to the knowledge base yet. Please ensure documents are loaded."
        
        try:
            response = self.rag_chain.invoke(question)
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
            self.vectorstore = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
            
            # Recreate RAG chain with ASU AI Platform
            if ASU_AI_API_TOKEN:
                self.llm = ASUAILM(
                    api_token=ASU_AI_API_TOKEN,
                    base_url=ASU_AI_BASE_URL,
                    model=ASU_AI_MODEL,
                    temperature=0.7
                )
                
                # Create RAG prompt template
                template = """Answer the question based only on the following context:

{context}

Question: {question}

Answer:"""
                prompt = ChatPromptTemplate.from_template(template)
                
                # Create RAG chain using LCEL (LangChain Expression Language)
                retriever = self.vectorstore.as_retriever(search_kwargs={"k": TOP_K_RESULTS})
                
                def format_docs(docs):
                    return "\n\n".join(doc.page_content for doc in docs)
                
                self.rag_chain = (
                    {"context": retriever | format_docs, "question": RunnablePassthrough()}
                    | prompt
                    | self.llm
                    | StrOutputParser()
                )  