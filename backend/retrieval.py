"""
Vector Database Retrieval using Pinecone
Implements product-specific document retrieval for RAG
Uses FREE local embeddings (sentence-transformers)
"""

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from config import settings

# Initialize Pinecone
pc = None
index = None

# Initialize local embedding model (FREE - no API needed!)
embedding_model = None

def initialize_pinecone(api_key: str, index_name: str = "product-manuals"):
    """Initialize Pinecone client and index"""
    global pc, index, embedding_model
    
    pc = Pinecone(api_key=api_key)
    
    # Initialize FREE local embedding model
    print("Loading local embedding model (one-time download)...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("[SUCCESS] Embedding model loaded!")
    
    # Create index if it doesn't exist
    # all-MiniLM-L6-v2 produces 384-dimensional vectors
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=384,  # MiniLM-L6-v2 dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"[SUCCESS] Created Pinecone index: {index_name}")
    
    index = pc.Index(index_name)
    return index


def get_embedding(text: str) -> List[float]:
    """
    Get embedding using FREE local model (sentence-transformers)
    No API calls, no cost!
    
    Args:
        text: Text to embed
    
    Returns:
        384-dimensional embedding vector
    """
    if embedding_model is None:
        raise RuntimeError("Embedding model not initialized. Call initialize_pinecone() first.")
    
    # Generate embedding using local model
    embedding = embedding_model.encode(text, convert_to_tensor=False)
    return embedding.tolist()


async def retrieve_documents(
    product_id: str, 
    query: str, 
    top_k: int = 3,
    namespace: Optional[str] = None
) -> str:
    """
    Retrieve relevant documents from Pinecone for a specific product
    
    Args:
        product_id: Product model ID (e.g., "VM-LI-48V-100AH")
        query: User's question
        top_k: Number of documents to retrieve
        namespace: Override namespace (defaults to "product_{product_id}")
    
    Returns:
        Concatenated retrieved documents as string
    """
    if index is None:
        return ""  # No index initialized
    
    # Use product-specific namespace
    ns = namespace or f"product_{product_id}"
    
    try:
        # Get query embedding using FREE local model
        query_embedding = get_embedding(query)
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=ns,
            include_metadata=True
        )
        
        # Extract and format documents
        if not results.matches:
            return ""  # No documents found
        
        documents = []
        for match in results.matches:
            # Include score for context
            score = match.score
            text = match.metadata.get("text", "")
            section = match.metadata.get("section", "")
            
            if text:
                documents.append(f"[{section}] {text} (relevance: {score:.2f})")
        
        return "\n\n".join(documents)
        
    except Exception as e:
        print(f"Retrieval error: {e}")
        return ""


def delete_namespace(product_id: str):
    """Delete all vectors for a specific product (useful for re-indexing)"""
    if index is None:
        return
    
    namespace = f"product_{product_id}"
    index.delete(delete_all=True, namespace=namespace)
    print(f"Deleted namespace: {namespace}")
