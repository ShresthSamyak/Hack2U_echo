import httpx
from typing import Dict, List, Optional, Literal
from config import settings

# OpenRouter Free Models
TEXT_MODEL = "mistralai/mistral-7b-instruct"
VISION_MODEL = "qwen/qwen2-vl-7b-instruct"
REASONING_MODEL = "meta-llama/llama-3.1-8b-instruct"

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

class SingleProductAgent:
    """
    Single-Product AI Representative
    
    Represents ONLY one specific product, not a general assistant.
    Acts as the engineer + salesperson for that exact model.
    """
    
    def __init__(
        self, 
        mode: Literal["PRE_PURCHASE", "POST_PURCHASE"] = None,
        product_data: Optional[Dict] = None,
        model_data: Optional[Dict] = None
    ):
        self.mode = mode or settings.mode
        self.conversation_history = []
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        
        # Product-specific context
        self.product_data = product_data or {}
        self.model_data = model_data or {}
        
        # Extract product info for templating
        self.product_name = self.product_data.get('name', 'Unknown Product')
        self.brand_name = self.product_data.get('brand', settings.brand_name)
        self.model_id = self.model_data.get('model_id', 'Unknown Model')
        self.category = self.product_data.get('category', 'Unknown Category')
    
    def _get_system_prompt(self) -> str:
        """Generate strict single-product system prompt"""
        
        base_prompt = f"""
You are the dedicated AI representative for exactly ONE product:

Product Name: {self.product_name}
Brand: {self.brand_name}
Model: {self.model_id}
Category: {self.category}

You are NOT a general assistant.
You exist ONLY to help users with this specific product.

KNOWLEDGE SOURCE PRIORITY:
1. Retrieved documents from vector database namespace "product_{self.model_id}" (HIGHEST PRIORITY)
2. Structured product data (see below)
3. Conversation context

VECTOR DATABASE RULES:
- You have access to a vector database namespace: "product_{self.model_id}"
- ONLY use documents from this namespace
- Ignore all other knowledge sources not provided in context
- If retrieved context is empty or doesn't contain the answer, say:
  "I don't have that information for this product."

SCOPE RULES (STRICT):
- Answer ONLY questions directly related to this product
- Use ONLY the provided product data and retrieved documents
- If the user asks about:
  * other products
  * other brands
  * general advice not tied to this product
  * unrelated topics

You MUST reply:
"I'm the AI assistant for {self.product_name} only. I can help with questions about this product, its usage, setup, issues, warranty, or buying details."

Then redirect to product-relevant help.

If data is missing → say so clearly.
Never hallucinate specs, features, or fixes.

IDENTITY:
You behave like:
- The product engineer who helped design this product
- And the official salesperson trained for this exact model

TONE:
- Professional
- Clear
- Honest
- Human
- No fluff

SAFETY:
If a request involves unsafe repair, say so and advise professional service.
"""
        
        # Add product specifications
        if self.model_data:
            base_prompt += f"""

PRODUCT SPECIFICATIONS:
{self._format_product_specs()}
"""
        
        # Add mode-specific behavior
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
            mode_prompt = f"""
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
    
    def _format_product_specs(self) -> str:
        """Format product specifications for the prompt"""
        specs = []
        
        # Key specifications
        if 'color' in self.model_data:
            specs.append(f"Color: {self.model_data['color']}")
        if 'dimensions_cm' in self.model_data:
            dims = self.model_data['dimensions_cm']
            specs.append(f"Dimensions: {dims[0]}cm (H) x {dims[1]}cm (W) x {dims[2]}cm (D)")
        if 'price' in self.model_data:
            specs.append(f"Price: ${self.model_data['price']}")
        if 'warranty_years' in self.model_data:
            specs.append(f"Warranty: {self.model_data['warranty_years']} years")
        if 'features' in self.model_data:
            specs.append(f"Features: {', '.join(self.model_data['features'])}")
        if 'installation' in self.model_data:
            specs.append(f"Installation: {self.model_data['installation']}")
        if 'maintenance' in self.model_data:
            specs.append(f"Maintenance: {self.model_data['maintenance']}")
        
        return '\n'.join(specs)
    
    def _check_scope(self, user_query: str) -> Optional[str]:
        """Check if query is about this specific product, return rejection if not"""
        
        # Keywords that suggest off-topic
        off_topic_indicators = [
            'other product', 'different brand', 'compare to', 'vs',
            'competitor', 'alternative', 'instead of', 'better than'
        ]
        
        query_lower = user_query.lower()
        
        # Check if asking about other products
        for indicator in off_topic_indicators:
            if indicator in query_lower and self.product_name.lower() not in query_lower:
                return f"I'm the AI assistant for {self.product_name} only. I can help with questions about this product, its usage, setup, issues, warranty, or buying details. What would you like to know about {self.product_name}?"
        
        return None
    
    async def _call_openrouter(
        self, 
        messages: List[Dict],
        model: str,
        temperature: float = 0.7
    ) -> str:
        """Call OpenRouter API"""
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1000,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def generate_response(
        self,
        user_query: str,
        rag_context: Optional[str] = None,
        room_analysis: Optional[str] = None,
        use_reasoning: bool = False
    ) -> str:
        """
        Generate agent response for this specific product
        
        Args:
            user_query: User's question
            rag_context: Retrieved documents (priority 1)
            room_analysis: Room image analysis if available
            use_reasoning: Use better reasoning model
        """
        
        # Check scope - reject off-topic questions
        scope_check = self._check_scope(user_query)
        if scope_check:
            return scope_check
        
        # Build system prompt
        system_content = self._get_system_prompt()
        
        # Add RAG context if provided (highest priority)
        if rag_context:
            system_content += f"\n\nRETRIEVED DOCUMENTS (Use this first):\n{rag_context}"
        
        # Add room analysis if available
        if room_analysis:
            system_content += f"\n\nROOM ANALYSIS:\n{room_analysis}"
        
        # Build messages
        messages = [{"role": "system", "content": system_content}]
        
        # Add conversation history (last 3 exchanges)
        for msg in self.conversation_history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current query
        messages.append({"role": "user", "content": user_query})
        
        # Choose model
        model = REASONING_MODEL if use_reasoning else TEXT_MODEL
        
        try:
            response = await self._call_openrouter(messages, model)
            
            # Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_query
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            return response
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    async def handle_error_code(self, error_code: str) -> str:
        """Handle error code for this specific product"""
        
        # Find error in model data
        common_issues = self.model_data.get('common_issues', [])
        
        for issue in common_issues:
            if issue.get('error', '').upper() == error_code.upper():
                error_context = f"""
ERROR CODE: {error_code}
MEANING: {issue.get('meaning')}
FIX: {issue.get('fix')}
"""
                return await self.generate_response(
                    f"I'm seeing error code {error_code}. What does this mean and how do I fix it?",
                    rag_context=error_context
                )
        
        # Error code not found
        return await self.generate_response(
            f"I'm seeing error code {error_code} on my {self.product_name}. What should I do?"
        )
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    def switch_mode(self, new_mode: Literal["PRE_PURCHASE", "POST_PURCHASE"]):
        """Switch agent mode"""
        self.mode = new_mode
    
    def update_product(self, product_data: Dict, model_data: Dict):
        """Update to a different product/model"""
        self.product_data = product_data
        self.model_data = model_data
        self.product_name = product_data.get('name', 'Unknown Product')
        self.brand_name = product_data.get('brand', settings.brand_name)
        self.model_id = model_data.get('model_id', 'Unknown Model')
        self.category = product_data.get('category', 'Unknown Category')
        self.reset_conversation()

# Global instance (will be initialized with specific product)
single_product_agent = None
