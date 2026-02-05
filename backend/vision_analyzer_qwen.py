"""
Vision Analyzer using OpenRouter API
Based on official OpenRouter documentation via Context7
Supports free vision models with proper authentication
"""

import requests
import json
import base64
from typing import Optional, Dict, Any
from config import settings

class QwenVisionAnalyzer:
    """
    Vision analysis using OpenRouter's free vision models
    Implementation from official OpenRouter docs
    """
    
    def __init__(self):
        """Initialize OpenRouter with API key"""
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Use FREE vision model - Google Gemini Flash 1.5 8B
        self.model = "google/gemini-flash-1.5-8b"
        
        if self.api_key:
            print(f"🔑 OpenRouter Vision initialized")
            print(f"✅ Using FREE model: {self.model}")
        else:
            print("❌ OpenRouter API Key is MISSING!")
    
    def _encode_image_to_base64(self, image_data: bytes) -> str:
        """
        Encode image bytes to base64 data URI
        Official format from OpenRouter docs
        """
        base64_image = base64.b64encode(image_data).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_image}"
        
    def _build_vision_prompt(self, product_name: str, model_id: str, category: str) -> str:
        """Build the system prompt for vision analysis"""
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
  "observations": ["observation 1", "observation 2", "observation 3"],
  "detected_environment": "description of the space/environment",
  "wall_color": "color if visible",
  "floor_color": "color if visible",
  "lighting": "bright/dim/natural/artificial",
  "visible_product_parts": ["part1", "part2"],
  "visible_issues": ["issue1", "issue2"],
  "installation_obstacles": ["obstacle1", "obstacle2"],
  "confidence": 0.85
}}

If the image is unrelated to the product, return:

{{
  "image_type": "unrelated",
  "reason": "brief explanation"
}}

Be precise. Be conservative. No extra text. Return ONLY the JSON."""

    def _validate_json_output(self, json_str: str) -> Optional[Dict[str, Any]]:
        """Validate and parse JSON output"""
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
            if "confidence" not in data:
                data["confidence"] = 0.7  # Default confidence
            
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
        Analyze an image using OpenRouter vision API
        Official implementation from OpenRouter docs
        """
        try:
            # Build system prompt
            prompt = self._build_vision_prompt(product_name, model_id, category)
            
            # Encode image to base64 data URI (official format)
            image_url = self._encode_image_to_base64(image_data)
            
            print(f"🔍 Analyzing image with OpenRouter (FREE)...")
            
            # Official OpenRouter API request format
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
            
            payload = {
                "model": self.model,
                "messages": messages
            }
            
            # Make request
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Check response
            if response.status_code != 200:
                error_msg = f"Status {response.status_code}: {response.text}"
                print(f"❌ OpenRouter API error: {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg
                }
            
            # Parse response
            result = response.json()
            vision_output = result['choices'][0]['message']['content']
            print(f"📄 OpenRouter raw output: {vision_output[:200]}...")
            
            # Validate JSON
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
