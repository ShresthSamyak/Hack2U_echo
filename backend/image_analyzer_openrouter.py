import httpx
import base64
from PIL import Image
import io
from typing import Dict

# OpenRouter Vision Model (Free)
VISION_MODEL = "qwen/qwen2-vl-7b-instruct"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

class OpenRouterRoomAnalyzer:
    """Analyze room images using OpenRouter's free vision model"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    async def _validate_image_relevance(self, image_base64: str) -> Dict:
        """
        Validate if the image is product-related before analysis.
        
        Only analyze images to assist with:
        - Installing this product
        - Placing this product in a room
        - Diagnosing this product
        - Identifying parts of this product
        
        Ignore unrelated objects.
        """
        from config import settings
        
        validation_prompt = f"""
Analyze this image and determine if it is relevant to {settings.brand_name} products (home appliances like washing machines, refrigerators, etc.).

This image should ONLY be analyzed if it shows:
1. A room or space where such products could be installed (kitchen, laundry room, etc.)
2. The product itself or its parts
3. Installation context for such products
4. Diagnostic information about such products

Ignore unrelated objects like people, landscapes, animals, vehicles, etc.

Respond with ONLY one word:
- "RELEVANT" if the image is appropriate for product analysis
- "IRRELEVANT" if the image is not related to {settings.brand_name} products
"""
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": validation_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": VISION_MODEL,
            "messages": messages,
            "max_tokens": 50,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    OPENROUTER_API_URL,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                validation_result = result["choices"][0]["message"]["content"].strip().upper()
                
                if "IRRELEVANT" in validation_result:
                    return {
                        "valid": False,
                        "message": f"I can only analyze images related to {settings.brand_name} products."
                    }
                
                return {"valid": True}
                
        except Exception as e:
            # If validation fails, allow the image through
            return {"valid": True}
    
    async def analyze_room_image(self, image_data: bytes) -> Dict:
        """
        Analyze a room image to extract:
        - Room type
        - Space dimensions  
        - Colors
        - Lighting
        - Placement recommendations
        """
        
        # Convert image to base64
        image = Image.open(io.BytesIO(image_data))
        
        # Resize if too large (to save bandwidth)
        if image.width > 1024 or image.height > 1024:
            image.thumbnail((1024, 1024))
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Validate image relevance first
        validation_result = await self._validate_image_relevance(image_base64)
        if not validation_result.get("valid"):
            return {
                "status": "error",
                "error": "Image not relevant",
                "message": validation_result.get("message")
            }
        
        analysis_prompt = """
Analyze this room image and provide the following information:

1. **Room Type**: Identify the room (kitchen, laundry room, bedroom, living room, etc.)

2. **Available Space**: 
   - Estimate floor space dimensions
   - Identify potential placement locations for appliances
   - Note space constraints

3. **Color Palette**:
   - Primary wall color (with hex code estimate if possible)
   - Floor color and material
   - Accent colors

4. **Lighting**:
   - Natural or artificial
   - Warm or cool temperature
   - Brightness level

5. **Existing Elements**:
   - Current appliances or furniture
   - Countertops or cabinets
   - Door and window positions

6. **Placement Recommendations**:
   - Best locations for placing an appliance
   - Space constraints or challenges
   - Ventilation considerations

7. **Safety Concerns**:
   - Proximity to water sources
   - Adequate clearance
   - Access to power outlets

IMPORTANT: Be explicit about what you can and cannot determine with certainty. 
If measurements are estimates, **clearly state "APPROXIMATE" or "ESTIMATED"**.

Provide your analysis in a clear, structured format.
"""
        
        disclaimer_note = "\n\n**IMPORTANT: All measurements and dimensions in this analysis are APPROXIMATE ESTIMATES based on visual assessment. Please verify actual measurements before making purchase decisions.**"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": analysis_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": VISION_MODEL,
            "messages": messages,
            "max_tokens": 1000,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    OPENROUTER_API_URL,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "status": "success",
                    "analysis": result["choices"][0]["message"]["content"] + disclaimer_note,
                    "confidence": "⚠️ IMPORTANT: This is an AI-based visual analysis. All measurements are APPROXIMATE ESTIMATES and should be verified before making any purchase or installation decisions."
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to analyze image. Please ensure the image is clear and try again."
            }
    
    async def recommend_color_match(self, room_analysis: str, available_colors: list) -> Dict:
        """Recommend best color variant based on room analysis"""
        
        color_prompt = f"""
Based on this room analysis:
{room_analysis}

Available product colors:
{', '.join([f"{c['color']} ({c['hex_color']})" for c in available_colors])}

Recommend the best color variant for this room, considering:
1. Harmony with existing wall and floor colors
2. Interior design best practices
3. How the color will make the space feel

Provide:
- Recommended color and why
- Alternative options
- Colors to avoid and why

Be honest if multiple colors could work well.
"""
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": "mistralai/mistral-7b-instruct",  # Use text model for this
            "messages": [
                {"role": "user", "content": color_prompt}
            ],
            "max_tokens": 500,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    OPENROUTER_API_URL,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "status": "success",
                    "recommendation": result["choices"][0]["message"]["content"]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def assess_product_fit(
        self, 
        room_analysis: str, 
        product_dimensions: list,
        product_category: str
    ) -> Dict:
        """Assess if a product will fit in the analyzed room"""
        
        fit_prompt = f"""
Based on this room analysis:
{room_analysis}

Product specifications:
- Category: {product_category}
- Dimensions: {product_dimensions[0]}cm (H) x {product_dimensions[1]}cm (W) x {product_dimensions[2]}cm (D)

Required clearances:
- Washing machine: 10cm sides, 15cm back
- Refrigerator: 10cm sides, 15cm back, 10cm top
- General appliances: minimum 5cm clearance

Assess:
1. Will this product fit in the available space?
2. Are there any clearance concerns?
3. What is the recommended placement location?
4. Any installation challenges?

Provide a clear YES/NO on whether it fits, followed by detailed reasoning.
Be conservative - if it's tight, warn the user.
"""
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct",  # Use reasoning model
            "messages": [
                {"role": "user", "content": fit_prompt}
            ],
            "max_tokens": 500,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    OPENROUTER_API_URL,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "status": "success",
                    "assessment": result["choices"][0]["message"]["content"]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Global instance
openrouter_room_analyzer = OpenRouterRoomAnalyzer()
