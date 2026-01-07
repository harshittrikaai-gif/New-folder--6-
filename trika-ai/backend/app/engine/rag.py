"""RAG Engine with ChromaDB vector store."""
import os
from typing import List, Dict, Any, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, 
    PyPDFLoader,
    UnstructuredMarkdownLoader
)
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from ..core.config import get_settings

settings = get_settings()


class RAGEngine:
    """RAG pipeline with document indexing and retrieval."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self._vectorstore: Optional[Chroma] = None
    
    @property
    def vectorstore(self) -> Chroma:
        """Get or create vector store connection."""
        if self._vectorstore is None:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=str(settings.chroma_port),
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )
            
            self._vectorstore = Chroma(
                client=client,
                collection_name=settings.chroma_collection,
                embedding_function=self.embeddings,
            )
        return self._vectorstore
    
    def _get_loader(self, file_path: str):
        """Get appropriate document loader based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            return PyPDFLoader(file_path)
        elif ext == ".md":
            return UnstructuredMarkdownLoader(file_path)
        else:
            return TextLoader(file_path)
    
    async def index_document(
        self, 
        file_path: str, 
        filename: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Index a document into the vector store."""
        # Load document
        loader = self._get_loader(file_path)
        documents = loader.load()
        
        # Add metadata
        for doc in documents:
            doc.metadata.update({
                "filename": filename,
                "source": file_path,
                **(metadata or {})
            })
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add to vector store
        ids = self.vectorstore.add_documents(chunks)
        
        return {
            "indexed": True,
            "chunks": len(chunks),
            "ids": ids
        }
    
    async def query(
        self, 
        query: str, 
        k: int = 5,
        filter: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Query the vector store for relevant documents."""
        results = self.vectorstore.similarity_search_with_score(
            query, 
            k=k,
            filter=filter
        )
        
        documents = []
        sources = []
        
        for doc, score in results:
            documents.append(doc.page_content)
            sources.append({
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata,
                "score": float(score)
            })
        
        return {
            "documents": documents,
            "sources": sources
        }
    
    async def remove_document(self, file_id: str) -> bool:
        """Remove a document from the vector store by file ID."""
        try:
            # ChromaDB delete by metadata filter
            self.vectorstore._collection.delete(
                where={"file_id": file_id}
            )
            return True
        except Exception:
            return False
    
    async def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            self.vectorstore._collection.delete()
            return True
        except Exception:
            return False
