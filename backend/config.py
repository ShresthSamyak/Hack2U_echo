from pydantic_settings import BaseSettings
from typing import Literal, Optional
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AI Configuration
    ai_provider: str = "openrouter"  # openrouter, gemini, or groq
    OPENROUTER_API_KEY: Optional[str] = None  # Optional - free tier works without key
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # Pinecone Configuration (for vector database)
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: str = "product-manuals"
    
    # OpenAI Configuration (for embeddings)
    openai_embedding_key: Optional[str] = None  # For text-embedding-ada-002
    
    # Operation Mode
    mode: Literal["PRE_PURCHASE", "POST_PURCHASE"] = "PRE_PURCHASE"
    
    # Default Product Configuration
    # These are defaults - actual product is set per-session
    brand_name: str = "echo"
    product_category: str = "home_appliances"
    default_product_id: Optional[str] = None  # e.g., "wm_2026_pro"
    default_model_id: Optional[str] = None    # e.g., "AT-WM-9KG-BLACK"
    
    # Supabase Configuration (PostgreSQL database)
    supabase_url: Optional[str] = None
    supabase_service_key: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    default_brand_id: Optional[str] = None
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Configuration
    frontend_url: str = "http://localhost:5173"
    
    class Config:
        # Use absolute path to .env file
        env_file = str(Path(__file__).parent / ".env")
        case_sensitive = False

settings = Settings()
