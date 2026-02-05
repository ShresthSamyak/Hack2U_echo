"""
Vision Analyzer using Groq Llama 3.2 Vision
Extracts structured JSON data from images for product-specific analysis
Uses Groq's free vision model - same API as text generation
"""

from groq import Groq
import json
from typing import Optional, Dict, Any
from config import settings
import base64

class GroqVisionAnalyzer:
    """
    Vision analysis agent that extracts structured information from images
    using Groq's Llama 3.2 90B Vision model (FREE)
    """
    
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=settings.groq_api_key)
        # Use Groq's current vision model (90b was decommissioned)
        self.model = "llama-3.2-11b-vision-preview"
        print(f"🔑 Groq Vision initialized with model: {self.model}")
        
    def _encode_image_to_base64(self, image_data: bytes) -> str:
        """Encode image bytes to base64 data URL"""
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
        """Analyze an image and extract structured information"""
        try:
            # Build system prompt
            prompt = self._build_vision_prompt(product_name, model_id, category)
            
            # Encode image to base64
            image_url = self._encode_image_to_base64(image_data)
            
            print(f"🔍 Analyzing image with Groq Vision...")
            
            # Call Groq Vision API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                temperature=0.5,
                max_tokens=1024
            )
            
            # Extract response
            vision_output = completion.choices[0].message.content
            print(f"📄 Groq raw output: {vision_output[:200]}...")
            
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
groq_vision_analyzer = GroqVisionAnalyzer()
