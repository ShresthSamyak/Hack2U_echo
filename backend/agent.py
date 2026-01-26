import google.generativeai as genai
from typing import Dict, List, Optional, Literal
from config import settings
from product_db import product_db

# Configure Gemini
genai.configure(api_key=settings.google_api_key)

class ProductAgent:
    """
    Product Intelligence Agent with dual-mode operation:
    - PRE_PURCHASE: Consultative salesperson
    - POST_PURCHASE: Technical support engineer
    """
    
    def __init__(self, mode: Literal["PRE_PURCHASE", "POST_PURCHASE"] = None):
        self.mode = mode or settings.mode
        self.model = genai.GenerativeModel('gemini-pro')
        self.conversation_history = []
    
    def _get_system_prompt(self) -> str:
        """Generate mode-specific system prompt"""
        
        base_prompt = f"""
You are a Product Intelligence Agent for {settings.brand_name}, acting as the official AI representative for our products.

KNOWLEDGE SOURCE PRIORITY:
1. Retrieved documents from vector database namespace "product_{{{{PRODUCT_ID}}}}" (HIGHEST PRIORITY)
2. Structured product data provided in context
3. Conversation history

VECTOR DATABASE RULES:
- You have access to a vector database namespace: "product_{{{{PRODUCT_ID}}}}"
- ONLY use documents from this namespace
- Ignore all other knowledge sources not provided in context
- If retrieved context is empty or doesn't contain the answer, say:
  "I don't have that information for this product."

CRITICAL RULES:
- NEVER hallucinate technical specifications
- If information is not in the product data or retrieved documents, explicitly say "I don't have that specific information"
- Be honest about product limitations
- Prioritize customer needs over making a sale
- Ask clarifying questions when needed
- Provide step-by-step instructions when relevant

Available product categories: {', '.join(product_db.get_all_categories())}
"""
        
        if self.mode == "PRE_PURCHASE":
            mode_prompt = """
MODE: PRE-PURCHASE (Official Product Salesperson)

You are acting as the official salesperson for the specific product being discussed.

YOUR TASK:
- Explain this product
- Determine if this product fits the user's needs
- Recommend the correct variant of THIS product (size, color, capacity, etc.)

QUESTION SCOPE - Ask ONLY questions necessary to evaluate:
- Space constraints
- Usage needs
- Budget compatibility
- Installation feasibility
- Aesthetic fit

HONESTY REQUIREMENT:
If this product is NOT suitable, say so clearly and explain why.

RECOMMENDATIONS:
- You may suggest "another model in this product line" (if provided in product data)
- Do NOT recommend competitors unless user explicitly asks

IMAGE ANALYSIS:
When an image is uploaded, analyze:
- Whether THIS product fits
- Placement recommendations
- Clearance requirements
- Color match with room
- Installation requirements

CRITICAL RULES:
- Do NOT discuss other products unless user explicitly requests
- Do NOT upsell unrelated items
- Your output must always stay tightly tied to this product
- Be honest about limitations and suitability

Sales style: Consultative, educational, trust-building through honesty
"""
        else:  # POST_PURCHASE
            mode_prompt = """
MODE: POST-PURCHASE (Technical Support Engineer)

You are acting as the technical support engineer for the specific product being discussed.

YOU MUST:
- Diagnose issues for this product
- Explain error codes for this product
- Guide setup and configuration
- Provide maintenance instructions
- Explain features of this product

PROCESS:
1. Identify the exact variant if possible
2. Reference official manual data
3. Provide step-by-step instructions
4. Include safety warnings when required

SAFETY REQUIREMENTS:
If the problem involves any of the following:
- Dangerous operations
- Internal electrical work
- Risks to warranty
- High voltage
- Gas connections
- Refrigerant
- Internal electronics

You MUST say clearly:
"This requires a certified service technician."

Then explain why it's dangerous.

IMAGE ANALYSIS:
If user uploads an image, use it to:
- Identify visible issues
- Confirm part location
- Verify installation

SCOPE LIMITS:
- Do NOT discuss other products
- Do NOT answer general appliance questions
- Stay strictly within this product

Tone: Calm, supportive, professional technician
NEVER blame the user - frame issues as normal troubleshooting
"""
        
        return base_prompt + "\n" + mode_prompt
    
    def _build_context(self, user_query: str, product_context: Optional[Dict] = None) -> str:
        """Build context for the AI model"""
        
        context_parts = [self._get_system_prompt()]
        
        # Add product context if provided
        if product_context:
            context_parts.append(f"\nRELEVANT PRODUCT INFORMATION:\n{product_context}")
        
        # Add conversation history
        if self.conversation_history:
            context_parts.append("\nCONVERSATION HISTORY:")
            for msg in self.conversation_history[-6:]:  # Last 3 exchanges
                context_parts.append(f"{msg['role'].upper()}: {msg['content']}")
        
        # Add current query
        context_parts.append(f"\nUSER: {user_query}")
        context_parts.append("\nAGENT:")
        
        return "\n".join(context_parts)
    
    async def generate_response(
        self,
        user_query: str,
        product_context: Optional[Dict] = None,
        room_analysis: Optional[str] = None,
        rag_context: Optional[str] = None
    ) -> str:
        """
        Generate agent response based on query and context
        
        Args:
            user_query: User's question or request
            product_context: Relevant product information from database
            room_analysis: Room image analysis if available
            rag_context: Retrieved documents from vector database (priority 1)
        """
        
        # Build complete context
        full_context = self._build_context(user_query, product_context)
        
        # Add RAG context if provided (highest priority - add first)
        if rag_context:
            full_context = f"RETRIEVED DOCUMENTS (Use this first):\n{rag_context}\n\n" + full_context
        
        # Add room analysis if available
        if room_analysis:
            full_context += f"\n\nROOM ANALYSIS:\n{room_analysis}"
        
        try:
            response = self.model.generate_content(full_context)
            agent_response = response.text
            
            # Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_query
            })
            self.conversation_history.append({
                "role": "agent",
                "content": agent_response
            })
            
            return agent_response
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
    
    async def handle_error_code(self, model_id: str, error_code: str) -> str:
        """Handle error code lookup and troubleshooting"""
        
        error_info = product_db.get_error_code_info(model_id, error_code)
        
        if not error_info:
            return await self.generate_response(
                f"I'm seeing error code {error_code} on model {model_id}. What does this mean and how do I fix it?"
            )
        
        # Build detailed response
        product_context = {
            "error_code": error_code,
            "meaning": error_info.get('meaning'),
            "fix": error_info.get('fix'),
            "model_id": model_id
        }
        
        return await self.generate_response(
            f"What does error code {error_code} mean and how do I fix it?",
            product_context=str(product_context)
        )
    
    async def recommend_products(
        self,
        category: str,
        requirements: Dict
    ) -> str:
        """Recommend products based on requirements"""
        
        # Get products from database
        products = product_db.get_category_products(category)
        
        if not products:
            return f"I apologize, but I don't have information about {category} products at the moment."
        
        recommendation_query = f"I'm looking for a {category} with these requirements: {requirements}"
        
        return await self.generate_response(
            recommendation_query,
            product_context=str(products)
        )
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    def switch_mode(self, new_mode: Literal["PRE_PURCHASE", "POST_PURCHASE"]):
        """Switch agent mode"""
        self.mode = new_mode
        # Optionally reset conversation when switching modes
        # self.reset_conversation()

# Global instance
agent = ProductAgent()
