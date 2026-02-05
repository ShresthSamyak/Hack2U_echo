"""
Groq-based Product Agent - Simple and Fast
Uses Groq's ultra-fast inference
"""

import requests
from typing import Optional, Dict
import json
import uuid
from config import settings

# Import database for persistent storage
try:
    from database import db
    DATABASE_AVAILABLE = db.enabled
except ImportError:
    DATABASE_AVAILABLE = False
    db = None

class GroqAgent:
    def __init__(self, mode: str = "PRE_PURCHASE", session_id: Optional[str] = None, user_id: Optional[str] = None):
        self.mode = mode
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "openai/gpt-oss-120b"  # GPT-OSS 120B - MoE with advanced reasoning
        self.conversation_history = []  # Fall back in-memory storage
        self.session_id = session_id or str(uuid.uuid4())
        self.brand_id = settings.default_brand_id
        self.user_id = user_id

        
        # Create conversation in database if available
        if DATABASE_AVAILABLE and self.brand_id:
            if not db.conversation_exists(self.session_id):
                db.create_conversation(
                    session_id=self.session_id,
                    brand_id=self.brand_id,
                    mode=self.mode,
                    user_id=self.user_id
                )
                print(f"✅ Conversation session: {self.session_id}")

    
    def switch_mode(self, new_mode: str):
        """Switch between PRE_PURCHASE and POST_PURCHASE modes"""
        self.mode = new_mode
        print(f"🔄 Switched to {new_mode} mode")
    
    def _get_system_prompt(self) -> str:
        """Get system prompt based on mode"""
        base_prompt = f"""You are a helpful product assistant for {settings.brand_name}.

STRICT PRODUCT SCOPE - CRITICAL RULES:
- You are bound to EXACTLY ONE product that the user is viewing
- If the user asks about OTHER products, OTHER brands, or UNRELATED topics:
  → Respond ONLY: "I'm the AI assistant for this product only. I can help with its buying, usage, or issues."
- Do NOT answer partially. Do NOT redirect to other products. Fail closed.
- This applies to ALL queries: text, images, pre-purchase, post-purchase

VECTOR DATABASE RULES:
- If RETRIEVED DOCUMENTS are provided, use them as your PRIMARY source
- Retrieved docs are product-specific and highest priority
- If no retrieved context and you don't know: say "I don't have that information for this product."

"""
        
        if self.mode == "PRE_PURCHASE":
            return base_prompt + """MODE: PRE_PURCHASE (Product Consultant)

YOUR ROLE: Official salesperson for this specific product

GUIDELINES:
- Explain this product's features and benefits
- Determine if it fits the user's needs
- Recommend the correct variant (size, color, capacity)
- Ask about space, budget, usage needs
- Be HONEST if product doesn't fit - explain why
- Recommend ONLY other variants of this product, not competitors
"""
        else:
            return base_prompt + """MODE: POST_PURCHASE (Technical Support)

YOUR ROLE: Technical support engineer for this product

GUIDELINES:
- Diagnose issues and explain error codes
- Guide through setup and installation
- Provide troubleshooting steps
- ⚠️ CRITICAL: For dangerous operations (electrical, gas, motors) say:
  "This requires a certified technician. Please do not attempt this."
- Use retrieved documents for accurate technical specs
"""
    
    async def generate_response(
        self,
        user_query: str,
        product_context: Optional[Dict] = None,
        rag_context: Optional[str] = None,
        vision_json: Optional[Dict] = None,
        language: str = "en"
    ) -> str:
        """Generate response using Groq with vision JSON support"""
        
        # Build system message
        system_content = self._get_system_prompt()
        
        # Add RAG context (highest priority)
        if rag_context:
            system_content += f"\n\nRETRIEVED DOCUMENTS (Use this first):\n{rag_context}"
        
        # Add product context if available
        if product_context and "model" in product_context:
            model = product_context["model"]
            product = product_context.get("product", {})
            
            system_content += f"\n\nPRODUCT INFORMATION:\n"
            system_content += f"Model: {model.get('model_id', 'Unknown')}\n"
            system_content += f"Product: {product.get('name', 'Unknown')}\n"
            
            if "features" in model:
                system_content += f"Features: {', '.join(model['features'])}\n"
            if "price" in model:
                system_content += f"Price: ${model['price']}\n"
            if "warranty_years" in model:
                system_content += f"Warranty: {model['warranty_years']} years\n"
            if "installation" in model:
                system_content += f"Installation: {model['installation']}\n"
            if "maintenance" in model:
                system_content += f"Maintenance: {model['maintenance']}\n"
            
            # Add error codes if available
            if "common_issues" in model and model["common_issues"]:
                system_content += f"\nCOMMON ERROR CODES:\n"
                for issue in model["common_issues"]:
                    system_content += f"- {issue['error']}: {issue['meaning']} - FIX: {issue['fix']}\n"
            
            # Add manual information if available
            if "manual" in model and isinstance(model["manual"], dict):
                manual = model["manual"]
                if "overview" in manual:
                    system_content += f"\nProduct Overview: {manual['overview']}\n"
                if "safety_guidelines" in manual:
                    system_content += f"\nSafety Guidelines: {', '.join(manual['safety_guidelines'][:3])}\n"


        # Add vision JSON if available (from Qwen2.5-VL)
        if vision_json:
            import json as json_lib
            
            # Check if it's multi-image or single image
            if "images_count" in vision_json:
                system_content += f"\n\n📷 VISION ANALYSIS (from {vision_json['images_count']} uploaded images):\n{json_lib.dumps(vision_json, indent=2)}"
                system_content += "\n\nIMPORTANT: The user uploaded multiple images. Use all the visual data from the analyses to provide comprehensive spatial and color recommendations."
            else:
                system_content += f"\n\n📷 VISION ANALYSIS (from uploaded image):\n{json_lib.dumps(vision_json, indent=2)}"
                system_content += "\n\nIMPORTANT: The user uploaded an image. Use this vision data for spatial, color, and installation recommendations."
            
            # Add confidence warning if low
            confidence = vision_json.get("confidence", vision_json.get("combined_confidence", 1.0))
            if confidence < 0.6:
                system_content += f"\n\n⚠️ Note: Vision analysis confidence is low ({confidence:.2f}). Be conservative with spatial recommendations."
        else:
            # No vision data - tell AI to answer normally from product specs
            system_content += """

🚫 NO IMAGES UPLOADED - TEXT-ONLY QUERY MODE

CRITICAL INSTRUCTIONS:
1. The user did NOT upload any images - they only sent a text question
2. DO NOT say "I'm not able to view images" or "I can't see what's shown"
3. DO NOT ask the user to upload images or describe what they see
4. ANSWER their question DIRECTLY using the PRODUCT INFORMATION and RETRIEVED DOCUMENTS provided above
5. If they ask about dimensions, warranty, features, price, etc. - answer from the product specs
6. ONLY mention uploading images if they specifically ask "Will this fit in my room?" or similar spatial questions

Example good response to "What is the warranty period?":
"This model comes with a {X}-year warranty covering..."

Example BAD response (DO NOT DO THIS):
"I'm not able to view images, so I can't see what's shown. Could you describe..."
"""
        
        # Add language instruction based on user preference
        if language == "hi":
            system_content += """

🌐 LANGUAGE INSTRUCTION - CRITICAL:
You MUST respond ENTIRELY in Hindi (हिंदी) using Devanagari script.
- All explanations, descriptions, and conversation should be in Hindi
- Product brand names (e.g., "AquaTech") can stay in English
- Numbers and technical specifications should use International numerals (1, 2, 3...)
- Use natural, conversational Hindi suitable for Indian customers

Example:
User: "वारंटी कितने साल की है?"
You: "यह मॉडल 2 साल की वारंटी के साथ आता है जिसमें इन्वर्टर मोटर 5 साल तक कवर होती है..."
"""
        else:
            system_content += """

🌐 LANGUAGE INSTRUCTION:
You MUST respond in English.
"""

        
        # Build messages
        messages = [{"role": "system", "content": system_content}]
        
        # Get conversation history from database or memory
        history = []
        if DATABASE_AVAILABLE:
            history = db.get_conversation_history(self.session_id, limit=6)
        if not history:
            # Fallback to in-memory
            history = self.conversation_history[-6:]
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current query
        messages.append({"role": "user", "content": user_query})
        
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            assistant_response = result["choices"][0]["message"]["content"]
            
            # Store conversation in database
            if DATABASE_AVAILABLE:
                db.add_message(self.session_id, "user", user_query)
                db.add_message(self.session_id, "assistant", assistant_response)
            
            # Also store in memory as fallback
            self.conversation_history.append({"role": "user", "content": user_query})
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
        
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."


# Create global agent instance
agent = GroqAgent(mode=settings.mode)
