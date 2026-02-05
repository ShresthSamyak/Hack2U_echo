"""
Database layer for Product Intelligence Agent
Uses Supabase (PostgreSQL) for persistent conversation storage
"""

from supabase import create_client, Client
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path
import os
import json

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

class Database:
    """Supabase database interface for conversation management"""
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            print("[WARNING] Supabase credentials not found. Database features disabled.")
            self.client = None
            self.enabled = False
        else:
            try:
                self.client: Client = create_client(supabase_url, supabase_key)
                self.enabled = True
                print("[SUCCESS] Supabase database connected!")
            except Exception as e:
                print(f"[ERROR] Supabase connection failed: {e}")
                self.client = None
                self.enabled = False
    
    # ==================== Conversation Management ====================
    
    def create_conversation(
        self,
        session_id: str,
        brand_id: str,
        mode: str = "PRE_PURCHASE",
        product_id: Optional[str] = None,
        model_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """Create a new conversation session"""
        if not self.enabled:
            return False
        
        try:
            self.client.table("conversations").insert({
                "session_id": session_id,
                "brand_id": brand_id,
                "mode": mode,
                "product_id": product_id,
                "model_id": model_id,
                "user_id": user_id,
                "messages": [],
                "metadata": {}
            }).execute()
            return True
        except Exception as e:
            print(f"Error creating conversation: {e}")
            return False
    
    def get_conversation(self, session_id: str) -> Optional[Dict]:
        """Retrieve conversation by session ID"""
        if not self.enabled:
            return None
        
        try:
            response = self.client.table("conversations")\
                .select("*")\
                .eq("session_id", session_id)\
                .execute()
            
            # Return first result or None if no results
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error retrieving conversation: {e}")
            return None
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 6
    ) -> List[Dict]:
        """Get last N messages from conversation"""
        if not self.enabled:
            return []
        
        try:
            conv = self.get_conversation(session_id)
            if not conv:
                return []
            
            messages = conv.get("messages", [])
            return messages[-limit:] if len(messages) > limit else messages
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> bool:
        """Add a message to conversation"""
        if not self.enabled:
            return False
        
        try:
            # Get current conversation
            conv = self.get_conversation(session_id)
            if not conv:
                return False
            
            messages = conv.get("messages", [])
            
            # Append new message
            messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Update conversation
            self.client.table("conversations")\
                .update({"messages": messages})\
                .eq("session_id", session_id)\
                .execute()
            
            return True
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    
    def update_conversation(
        self,
        session_id: str,
        messages: List[Dict]
    ) -> bool:
        """Update entire message history"""
        if not self.enabled:
            return False
        
        try:
            self.client.table("conversations")\
                .update({"messages": messages})\
                .eq("session_id", session_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error updating conversation: {e}")
            return False
    
    # ==================== Analytics ====================
    
    def log_analytics(
        self,
        brand_id: str,
        event_type: str,
        user_query: Optional[str] = None,
        product_id: Optional[str] = None,
        mode: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        error_occurred: bool = False,
        error_message: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> bool:
        """Log analytics event"""
        if not self.enabled:
            return False
        
        try:
            self.client.table("analytics").insert({
                "brand_id": brand_id,
                "conversation_id": conversation_id,
                "product_id": product_id,
                "mode": mode,
                "event_type": event_type,
                "user_query": user_query,
                "response_time_ms": response_time_ms,
                "error_occurred": error_occurred,
                "error_message": error_message
            }).execute()
            return True
        except Exception as e:
            print(f"Error logging analytics: {e}")
            return False
    
    # ==================== Helper Methods ====================
    
    def conversation_exists(self, session_id: str) -> bool:
        """Check if conversation exists"""
        return self.get_conversation(session_id) is not None
    
    def delete_conversation(self, session_id: str) -> bool:
        """Delete conversation (for testing/cleanup)"""
        if not self.enabled:
            return False
        
        try:
            self.client.table("conversations")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    def list_conversations(
        self,
        user_id: str,
        model_id: Optional[str] = None,
        mode: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """List conversations for user, optionally filtered by product/mode"""
        if not self.enabled:
            return []
        
        try:
            query = self.client.table("conversations")\
                .select("*")\
                .eq("user_id", user_id)
            
            if model_id:
                query = query.eq("model_id", model_id)
            if mode:
                query = query.eq("mode", mode)
            
            response = query\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"Error listing conversations: {e}")
            return []


# Global database instance
db = Database()
