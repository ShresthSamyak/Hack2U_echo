from google import genai
from google.genai import types
from PIL import Image
import io
import base64
from typing import Dict, Optional
from config import settings

# Configure Gemini with new SDK
client = genai.Client(api_key=settings.google_api_key)

class RoomAnalyzer:
    """Analyze room images for product placement and color matching"""
    
    def __init__(self):
        # Model name for the new SDK
        self.model_name = 'gemini-1.5-flash'
    
    async def _validate_image_relevance(self, image: Image.Image) -> Dict:
        """
        Validate if the image is product-related before analysis.
        
        Only analyze images to assist with:
        - Installing this product
        - Placing this product in a room
        - Diagnosing this product
        - Identifying parts of this product
        
        Ignore unrelated objects.
        """
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
        
        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=[validation_prompt, image]
            )
            result = response.text.strip().upper()
            
            if "IRRELEVANT" in result:
                return {
                    "valid": False,
                    "message": f"I can only analyze images related to {settings.brand_name} products."
                }
            
            return {"valid": True}
            
        except Exception as e:
            # If validation fails, allow the image through but log the error
            return {"valid": True}
    
    async def analyze_room_image(self, image_data: bytes) -> Dict:
        """
        Analyze a room image to extract:
        - Room type (kitchen, laundry, bedroom, etc.)
        - Approximate free space
        - Wall colors
        - Floor colors
        - Lighting temperature
        - Existing appliances
        - Door/window positions
        """
        
        # Convert image bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Validate image relevance first
        validation_result = await self._validate_image_relevance(image)
        if not validation_result.get("valid"):
            return {
                "status": "error",
                "error": "Image not relevant",
                "message": validation_result.get("message")
            }
        
        analysis_prompt = """
Analyze this room image and provide the following information in a structured format:

1. **Room Type**: Identify the room type (kitchen, laundry room, bedroom, living room, garage, etc.)

2. **Available Space**: 
   - Estimate approximate floor space dimensions
   - Identify potential placement locations for appliances
   - Note any space constraints (tight corners, narrow areas)

3. **Color Palette**:
   - Primary wall color (and hex code estimate if possible)
   - Floor color and material
   - Accent colors present

4. **Lighting**:
   - Natural or artificial lighting
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
   - Proximity to water sources (for electrical appliances)
   - Adequate clearance
   - Access to power outlets

IMPORTANT: Be explicit about what you can and cannot determine with certainty. 
If measurements are estimates, **clearly state "APPROXIMATE" or "ESTIMATED"**.
If something is unclear from the image, say so.

Provide your analysis in a clear, structured format.
"""
        
        disclaimer_note = "\n\n**IMPORTANT: All measurements and dimensions in this analysis are APPROXIMATE ESTIMATES based on visual assessment. Please verify actual measurements before making purchase decisions.**"
        
        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=[analysis_prompt, image]
            )
            
            return {
                "status": "success",
                "analysis": response.text + disclaimer_note,
                "confidence": "⚠️ IMPORTANT: This is an AI-based visual analysis. All measurements are APPROXIMATE ESTIMATES and should be verified before making any purchase or installation decisions."
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to analyze image. Please ensure the image is clear and shows the room."
            }
    
    async def recommend_color_match(self, room_analysis: str, available_colors: list) -> Dict:
        """
        Based on room analysis, recommend the best color variant
        
        Args:
            room_analysis: Text analysis of the room
            available_colors: List of available product colors with hex codes
        """
        
        color_prompt = f"""
Based on this room analysis:
{room_analysis}

Available product colors:
{', '.join([f"{c['color']} ({c['hex_color']})" for c in available_colors])}

Recommend the best color variant for this room, considering:
1. Harmony with existing wall and floor colors
2. Interior design best practices
3. How the color will make the space feel (larger, cozier, modern, etc.)

Provide:
- Recommended color and why
- Alternative options
- Colors to avoid and why

Be honest if multiple colors could work well.
"""
        
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=color_prompt
            )
            
            return {
                "status": "success",
                "recommendation": response.text
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
        """
        Assess if a product will physically fit in the analyzed room
        
        Args:
            room_analysis: Text analysis of the room
            product_dimensions: [height, width, depth] in cm
            product_category: Type of product (washing_machine, refrigerator, etc.)
        """
        
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
4. Any installation challenges (door swing, access, etc.)?

Provide a clear YES/NO on whether it fits, followed by detailed reasoning.
Be conservative - if it's tight, warn the user.
"""
        
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=fit_prompt
            )
            
            return {
                "status": "success",
                "assessment": response.text
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Global instance
room_analyzer = RoomAnalyzer()
