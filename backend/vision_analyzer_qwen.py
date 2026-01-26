"""
Vision Analyzer using Qwen2.5-VL-7B-Instruct via OpenRouter
Extracts structured JSON data from images for product-specific analysis
"""

from openai import OpenAI
import json
import base64
from typing import Optional, Dict, Any
from config import settings

class QwenVisionAnalyzer:
    """
    Vision analysis agent that extracts structured information from images
    using Qwen2.5-VL-7B-Instruct model via OpenRouter
    """
    
    def __init__(self):
        """Initialize OpenRouter client for Qwen2.5-VL"""
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key
        )
        self.model = "qwen/qwen-2.5-vl-7b-instruct:free"
        
    def _build_vision_prompt(self, product_name: str, model_id: str, category: str) -> str:
        """
        Build the system prompt for Qwen vision analysis
        
        Args:
            product_name: Name of the product
            model_id: Model identifier
            category: Product category
            
        Returns:
            Formatted system prompt for vision extraction
        """
        return f"""You are a vision analysis agent for a product-specific AI assistant.

The user has uploaded an image related to this product:

Product Name: {product_name}
Model: {model_id}
Category: {category}

Your task:

Analyze the image ONLY to extract information useful for:

- Product placement
- Installation compatibility
- Size fitting
- Color matching
- Visible damage
- Error diagnosis
- Part identification

STRICT RULES:

- Do NOT answer the user directly.
- Do NOT provide advice.
- Do NOT mention other products.
- Do NOT hallucinate measurements.
- If unsure, say "unknown".

Return ONLY valid JSON in this format:

{{
  "image_type": "room | product | installation | damage | error_display | other",
  "detected_environment": "",
  "approx_space_cm": {{ "width": null, "height": null, "depth": null }},
  "wall_color": "",
  "floor_color": "",
  "lighting": "",
  "visible_product_parts": [],
  "visible_issues": [],
  "visible_error_codes": [],
  "installation_obstacles": [],
  "confidence": 0.0
}}

If the image is unrelated to the product, return:

{{
  "image_type": "unrelated",
  "reason": "..."
}}

Be precise. Be conservative. No extra text."""

    def _encode_image_to_base64(self, image_data: bytes) -> str:
        """
        Encode image bytes to base64 data URL
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Base64 encoded data URL
        """
        b64_image = base64.b64encode(image_data).decode('utf-8')
        return f"data:image/jpeg;base64,{b64_image}"
    
    def _validate_json_output(self, json_str: str) -> Optional[Dict[str, Any]]:
        """
        Validate and parse JSON output from Qwen
        
        Args:
            json_str: JSON string from model
            
        Returns:
            Parsed JSON dict or None if invalid
        """
        try:
            # Remove markdown code blocks if present
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            data = json.loads(json_str)
            
            # Validate required fields
            if "image_type" not in data:
                return None
            
            # If unrelated, just need reason
            if data["image_type"] == "unrelated":
                return data if "reason" in data else None
            
            # For other types, validate structure
            required_fields = ["detected_environment", "confidence"]
            if not all(field in data for field in required_fields):
                return None
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse vision JSON: {e}")
            return None
    
    async def analyze_image(
        self,
        image_data: bytes,
        product_name: str,
        model_id: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Analyze an image and extract structured information
        
        Args:
            image_data: Raw image bytes
            product_name: Product name for context
            model_id: Model ID for context
            category: Product category
            
        Returns:
            Dictionary with vision analysis results
        """
        try:
            # Build system prompt
            system_prompt = self._build_vision_prompt(product_name, model_id, category)
            
            # Encode image
            image_url = self._encode_image_to_base64(image_data)
            
            print(f"🔍 Analyzing image with Qwen2.5-VL...")
            
            # Call Qwen2.5-VL via OpenRouter
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://product-intelligence-agent.com",
                    "X-Title": "Product Intelligence Agent"
                },
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image and return the structured JSON."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,  # Low temperature for consistent JSON output
                max_tokens=1000
            )
            
            # Extract response
            vision_output = completion.choices[0].message.content
            print(f"📄 Qwen raw output: {vision_output[:200]}...")
            
            # Parse and validate JSON
            vision_json = self._validate_json_output(vision_output)
            
            if vision_json:
                print(f"✅ Vision analysis complete (confidence: {vision_json.get('confidence', 'N/A')})")
                return {
                    "status": "success",
                    "vision_data": vision_json,
                    "raw_output": vision_output
                }
            else:
                print(f"⚠️ Invalid JSON from vision model")
                return {
                    "status": "error",
                    "message": "Failed to parse vision output",
                    "raw_output": vision_output
                }
                
        except Exception as e:
            print(f"❌ Vision analysis error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

# Global instance
qwen_vision_analyzer = QwenVisionAnalyzer()
