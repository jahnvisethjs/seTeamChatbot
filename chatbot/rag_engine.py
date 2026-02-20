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
    ASU_AI_BASE_URL, ASU_AI_QUERY_V2_URL
)
from chatbot.utils import load_markdown_file, ensure_directory_exists

class ASUAILM(Runnable):
    """Custom LLM wrapper for ASU AI Platform API with correct header format."""
    
    def __init__(self, api_token: str, base_url: str, model: str, temperature: float = 0.7, max_tokens: int = 16000):
        self.api_token = api_token
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = ASU_AI_QUERY_V2_URL
    
    def invoke_vision(self, text_query: str, image_base64: str, mime_type: str = "image/png") -> str:
        """Invoke the ASU AI vision endpoint with a text query and base64-encoded image.
        
        Args:
            text_query: The text prompt/question about the image.
            image_base64: Raw base64-encoded image data (no data URI prefix).
            mime_type: MIME type of the image (default: "image/png").
        
        Returns:
            The API response text.
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # The ASU AI API requires the data URI prefix on the base64 data
        if not image_base64.startswith("data:"):
            image_data_uri = f"data:{mime_type};base64,{image_base64}"
        else:
            image_data_uri = image_base64
        
        payload = {
            "action": "query",
            "endpoint": "vision",
            "query": text_query,
            "image_file": image_data_uri,
            "model_provider": "openai",
            "model_name": "gpt4o"
        }
        
        try:
            print(f"DEBUG: Vision request - query: '{text_query[:100]}...', image_file length: {len(image_data_uri)} chars")

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=90)
            
            if response.status_code != 200:
                print(f"DEBUG: Vision API Error {response.status_code}: {response.text[:500]}")
                return f"Vision API error ({response.status_code}): {response.text[:300]}"
            
            result = response.json()
            
            if "response" in result:
                return result["response"]
            elif "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "message" in result:
                if isinstance(result["message"], dict):
                    return result["message"].get("content", str(result["message"]))
                return result["message"]
            else:
                return str(result)
                
        except requests.exceptions.Timeout:
            return "The vision request timed out. Please try again with a smaller image."
        except Exception as e:
            print(f"DEBUG: Vision exception: {str(e)}")
            return f"Error calling vision API: {str(e)}"
    
    def invoke(self, input_data: Any, config: Dict = None) -> str:
        """Invoke the LLM with the given input."""
        # Extract the query string/content from different input types
        query = None
        if isinstance(input_data, str):
            query = input_data
        elif isinstance(input_data, list):
            # Check if it's a list of LangChain messages (SystemMessage + HumanMessage)
            # If so, combine them into a single query to preserve system prompt context
            from langchain_core.messages import SystemMessage
            system_parts = []
            human_parts = []
            multimodal_content = None  # Track multimodal (image) content
            is_message_list = False
            for msg in input_data:
                if isinstance(msg, SystemMessage):
                    system_parts.append(msg.content if isinstance(msg.content, str) else str(msg.content))
                    is_message_list = True
                elif isinstance(msg, HumanMessage):
                    is_message_list = True
                    # Check if content is multimodal (list with text + image_url)
                    if isinstance(msg.content, list):
                        # This is multimodal content (e.g., text + image) — preserve as-is
                        multimodal_content = msg.content
                    else:
                        human_parts.append(msg.content if isinstance(msg.content, str) else str(msg.content))
                elif isinstance(msg, dict) and msg.get("role") == "user":
                    human_parts.append(msg["content"])
                    is_message_list = True
            
            if is_message_list:
                if multimodal_content is not None:
                    # For multimodal messages, prepend any system prompt as text
                    # and pass the full list structure to the API
                    if system_parts:
                        system_text = "\n\n".join(system_parts)
                        # Prepend system prompt to the multimodal content
                        query = [{"type": "text", "text": system_text}] + multimodal_content
                    else:
                        query = multimodal_content
                elif system_parts or human_parts:
                    # Text-only messages: combine system + human into single string
                    combined = ""
                    if system_parts:
                        combined += "\n\n".join(system_parts) + "\n\n"
                    if human_parts:
                        combined += "\n\n".join(human_parts)
                    query = combined.strip()
            else:
                # Fallback: use the last element
                if input_data:
                    query = str(input_data[-1])
        elif isinstance(input_data, dict) and "messages" in input_data:
            # Extract last user message
            messages = input_data["messages"]
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    query = msg["content"]
                    break
            if query is None and messages:
                query = str(messages[-1])
        else:
            # Assume it's a prompt value from ChatPromptTemplate
            query = str(input_data)
        
        if query is None:
            query = ""

        # Make API request with correct header format
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Determine if this is a multimodal (vision) request
        is_multimodal = isinstance(query, list)
        
        # Build model_params — only include max_tokens for text-only queries
        model_params = {
            "temperature": self.temperature
        }
        if not is_multimodal:
            model_params["max_tokens"] = self.max_tokens
        
        # For multimodal content, use OpenAI-compatible messages format
        # For text-only, use the simple query format
        # Build payload using the user-provided structure
        if is_multimodal:
            # Extract text and base64 image from the list structure
            text_query = ""
            image_base64 = ""
            for item in query:
                if item.get("type") == "text":
                    text_query = item.get("text", "")
                elif item.get("type") == "image_url":
                    image_url = item.get("image_url", {}).get("url", "")
                    if "base64," in image_url:
                        # Extract just the data part from the data URI
                        image_base64 = image_url.split("base64,")[1]
                    else:
                        image_base64 = image_url
            
            payload = {
                "action": "query",
                "endpoint": "vision",
                "query": text_query,
                "image_file": image_base64,
                "model_provider": "openai",
                "model_name": "gpt4o" # As specified in the example
            }
        else:
            payload = {
                "action": "query",
                "query": query,
                "model_provider": "openai",
                "model_name": self.model,
                "model_params": model_params
            }
        
        try:
            # Debugging: Log payload structure (truncate large strings for readability)
            debug_payload = {k: v for k, v in payload.items()}
            
            # Truncate content for logging
            if is_multimodal:
                debug_payload["query"] = "[multimodal content with image]"
            elif isinstance(payload.get("query"), str) and len(payload["query"]) > 200:
                debug_payload["query"] = payload["query"][:200] + "...[truncated]"
            
            print(f"DEBUG: Sending to ASU AI ({'multimodal/messages' if is_multimodal else 'text/query'} format): {str(debug_payload)[:500]}...")

            # Use a generous timeout — agenda generation can take several minutes
            timeout = 300  # 5 minutes
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=timeout)
            
            if response.status_code != 200:
                print(f"DEBUG: API Error {response.status_code}: {response.text[:500]}")

            if response.status_code == 500:
                # Provide a more helpful message for 500 errors in multimodal contexts
                if is_multimodal:
                    return f"The ASU AI API returned a 500 error. Raw response: {response.text}. This often happens if the image is too large or the payload structure is not supported by the platform's vision proxy. I've attempted to resize the image, but you might want to try a smaller or simpler file, or paste the text instead."
                return f"ASU AI API returned a 500 (Internal Server Error). Raw response: {response.text}"
                
            response.raise_for_status()
            
            result = response.json()
            
            # Extract content from ASU AI Platform response
            if "response" in result:
                return result["response"]
            elif "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "message" in result:
                if isinstance(result["message"], dict):
                    return result["message"].get("content", str(result["message"]))
                return result["message"]
            else:
                return str(result)
                
        except requests.exceptions.HTTPError as e:
            raise Exception(f"ASU AI API error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.Timeout:
            return "The request to ASU AI API timed out. This can happen with large images or slow connections. Please try again with a smaller file."
        except Exception as e:
            print(f"DEBUG: Exception: {str(e)}")
            raise Exception(f"Error calling ASU AI API: {str(e)}")

class RAGEngine:
    def __init__(self):
        # Use HuggingFace embeddings (local) since ASU AI embeddings endpoint has issues
        # Keep ASU AI for chat completions with GPT-5
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception as e:
            print(f"Warning: Could not load HuggingFace embeddings: {e}")
            print("Falling back to basic embeddings...")
            self.embeddings = None
            
        self.vectorstore = None
        self.llm = None
        self.rag_chain = None
        self.documents = []
        
    def load_documents(self, directory_path: str) -> None:
        """Load documents from a directory."""
        if not os.path.exists(directory_path):
            return
            
        # Recursive function to load files
        for root, _, files in os.walk(directory_path):
            for file_name in files:
                full_path = os.path.join(root, file_name)
                
                # Load markdown files
                if file_name.endswith('.md'):
                    content = load_markdown_file(full_path)
                    if content:
                        self.documents.append(Document(
                            page_content=content,
                            metadata={"source": file_name}
                        ))
                
                # Load text files
                elif file_name.endswith('.txt'):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            self.documents.append(Document(
                                page_content=content,
                                metadata={"source": file_name}
                            ))
                    except Exception as e:
                        print(f"Error loading {file_name}: {e}")
                
                # Load PDF files
                elif file_name.endswith('.pdf'):
                    try:
                        from langchain_community.document_loaders import PyPDFLoader
                        loader = PyPDFLoader(full_path)
                        pages = loader.load()
                        self.documents.extend(pages)
                    except Exception as e:
                        print(f"Error loading PDF {file_name}: {e}")
    
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