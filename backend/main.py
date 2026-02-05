from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal, List
import uvicorn
from contextlib import asynccontextmanager

from config import settings
from product_db import product_db
from database import db  # Supabase database

# Import retrieval module for RAG
try:
    from retrieval import initialize_pinecone, retrieve_documents
    RETRIEVAL_AVAILABLE = True
except ImportError:
    RETRIEVAL_AVAILABLE = False
    print("[WARNING] Retrieval module not available. Install: pip install sentence-transformers pinecone-client")

# Import based on AI provider
if settings.ai_provider == "openrouter":
    from agent_openrouter import SingleProductAgent
    from image_analyzer_openrouter import openrouter_room_analyzer as room_analyzer
elif settings.ai_provider == "groq":
    from agent_groq import agent
    from image_analyzer import room_analyzer  # Use Gemini for images, Groq for text
    SingleProductAgent = type(None)  # For isinstance checks
else:
    from agent import agent
    from image_analyzer import room_analyzer
    # Import SingleProductAgent for isinstance checks even when using Gemini
    try:
        from agent_openrouter import SingleProductAgent
    except ImportError:
        SingleProductAgent = type(None)  # Fallback if not available

# Initialize agent with default product if specified
if settings.ai_provider == "openrouter":
    agent = None  # Will be initialized below
    # Get default product/model from settings
    if settings.default_product_id and settings.default_model_id:
        result = product_db.get_model_by_id(settings.default_model_id)
        if result:
            product_data, model_data = result
            agent = SingleProductAgent(
                mode=settings.mode,
                product_data=product_data,
                model_data=model_data
            )
    
    # If no default, create with empty data (will be set per request)
    if not agent:
        agent = SingleProductAgent(mode=settings.mode)
# For Groq and Gemini,agent is already imported from their respective modules

from contextlib import asynccontextmanager

# Define lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application"""
    # Startup: Initialize Pinecone
    if RETRIEVAL_AVAILABLE and settings.pinecone_api_key:
        try:
            print("[INFO] Initializing Pinecone vector database...")
            initialize_pinecone(
                api_key=settings.pinecone_api_key,
                index_name=settings.pinecone_index_name
            )
            print("[SUCCESS] Pinecone initialized successfully!")
        except Exception as e:
            print(f"[WARNING] Pinecone initialization failed: {e}")
            print("   RAG functionality will be limited.")
    yield
    # Shutdown logic can go here if needed

app = FastAPI(
    title="Product Intelligence Agent API",
    description="Dual-mode AI assistant for pre-purchase consultation and post-purchase support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    model_id: Optional[str] = None
    category: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    mode: str
    suggestions: Optional[List[str]] = None
    vision_data: Optional[dict] = None

class ModeSwitch(BaseModel):
    mode: Literal["PRE_PURCHASE", "POST_PURCHASE"]

class ProductQuery(BaseModel):
    category: str
    requirements: Optional[dict] = None

class ErrorCodeQuery(BaseModel):
    model_id: str
    error_code: str

class RoomAnalysisResponse(BaseModel):
    status: str
    analysis: str
    confidence: str
    color_recommendation: Optional[dict] = None

# Routes
# Routes
@app.get("/test")
async def test():
    """Minimal test endpoint - no agent dependency"""
    return {"status": "ok", "message": "Backend is alive"}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Product Intelligence Agent",
        "mode": agent.mode if agent else settings.mode,
        "brand": settings.brand_name,
        "ai_provider": settings.ai_provider
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(
    message: Optional[str] = Form(None),
    model_id: Optional[str] = Form(None),
    mode: str = Form("PRE_PURCHASE"),
    conversation_id: Optional[str] = Form(None),
    language: str = Form("en"),
    user_id: Optional[str] = Form(None),
    images: List[UploadFile] = File([])
):

    """
    Main chat endpoint for conversational interaction
    Supports both text-only (Form/JSON) and text+image (multipart) requests
    """
    try:
        # STAGE 1: Process uploaded images with Gemini Vision (if present)
        vision_json = None
        if images and len(images) > 0:
            try:
                print(f"📷 Stage 1: Analyzing {len(images)} image(s) with OpenRouter (FREE)")
                # Get product context for vision analysis
                product_name = "Unknown Product"
                category = "appliance"
                
                if model_id:
                    result = product_db.get_model_by_id(model_id)
                    if result:
                        product_data, model_data = result
                        product_name = f"{product_data.get('brand', '')} {product_data.get('name', '')}"
                        category = product_data.get('category', 'appliance')
                
                # Import and use OpenRouter vision (FREE model)
                from vision_analyzer_qwen import qwen_vision_analyzer
                
                # Process each image (max 3)
                vision_results = []
                for idx, image in enumerate(images[:3]):
                    print(f"  🔍 Analyzing image {idx + 1}/{min(len(images), 3)}: {image.filename}")
                    image_data = await image.read()
                    vision_result = await qwen_vision_analyzer.analyze_image(
                        image_data=image_data,
                        product_name=product_name,
                        model_id=model_id or "unknown",
                        category=category
                    )
                    
                    if vision_result["status"] == "success":
                        vision_results.append(vision_result["vision_data"])
                
                # Merge vision results
                if vision_results:
                    if len(vision_results) == 1:
                        vision_json = vision_results[0]
                        print(f"✅ Stage 1 Complete: 1 image analyzed (confidence: {vision_json.get('confidence', 'N/A')})")
                    else:
                        # Combine multiple vision analyses
                        vision_json = {
                            "images_count": len(vision_results),
                            "analyses": vision_results,
                            "combined_confidence": sum([v.get("confidence", 0) for v in vision_results]) / len(vision_results)
                        }
                        print(f"✅ Stage 1 Complete: {len(vision_results)} images analyzed (avg confidence: {vision_json['combined_confidence']:.2f})")
                else:
                    print(f"⚠️ Stage 1: No successful vision analyses")
                    
            except Exception as e:
                print(f"❌ Vision analysis error: {e}")
                # Continue without vision JSON rather than failing
        
        # For single-product agents (OpenRouter only), update product context if model_id provided
        if isinstance(agent, SingleProductAgent) and model_id:
            result = product_db.get_model_by_id(model_id)
            if result:
                product_data, model_data = result
                agent.update_product(product_data, model_data)
        
        # Get product context for Groq agent (always fetch if model_id provided)
        product_context = None
        if model_id:
            result = product_db.get_model_by_id(model_id)
            if result:
                product_context = {"product": result[0], "model": result[1]}
                print(f"📦 Product context loaded: {result[0].get('name', 'Unknown')}")
        
        # Retrieve relevant documents from vector database if model_id provided
        rag_context = None
        if model_id and RETRIEVAL_AVAILABLE and settings.pinecone_api_key:
            try:
                rag_context = await retrieve_documents(
                    product_id=model_id,
                    query=message or "product information",
                    top_k=3
                )
                if rag_context:
                    print(f"📚 Retrieved RAG context: {len(rag_context)} chars")
            except Exception as e:
                print(f"⚠️ RAG retrieval failed: {e}")
                rag_context = None
        
        # STAGE 2: Generate response with Groq AI
        print(f"🧠 Stage 2: Generating response with Groq AI...")
        if isinstance(agent, SingleProductAgent):
            # SingleProductAgent (OpenRouter) accepts room_analysis parameter
            response = await agent.generate_response(
                user_query=message or "[User sent an image]",
                rag_context=rag_context,
                room_analysis=vision_json  #  Pass vision JSON
            )
        else:
            # Groq agent - pass vision JSON directly
            response = await agent.generate_response(
                user_query=message or "[User sent an image]",
                product_context=product_context,
                rag_context=rag_context,
                vision_json=vision_json,
                language=language
            )
        
        print(f"✅ Stage 2 Complete: Response generated")
        
        # Generate helpful suggestions based on mode
        suggestions = []
        if agent.mode == "PRE_PURCHASE":
            suggestions = [
                "Will this fit in my space?",
                "What's the warranty?",
                "Installation requirements?",
                "Color options?"
            ]
        else:
            suggestions = [
                "How do I install this?",
                "Troubleshoot an error",
                "Maintenance schedule",
                "User manual"
            ]
        
        
        return ChatResponse(
            response=response,
            mode=agent.mode,
            suggestions=suggestions,
            vision_data=vision_json
        )

    
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
async def get_conversation_history(session_id: str):
    """
    Retrieve conversation history for a session
    Enables session persistence - users can reload and continue conversations
    """
    try:
        if db.enabled:
            history = db.get_conversation_history(session_id, limit=50)
            print(f"📚 Retrieved {len(history)} messages for session: {session_id}")
            return {
                "session_id": session_id,
                "messages": history
            }
        else:
            return {
                "session_id": session_id,
                "messages": []
            }
    except Exception as e:
        print(f"⚠️ Error retrieving history for {session_id}: {e}")
        return {
            "session_id": session_id,
            "messages": []
        }

@app.get("/conversations/list")
async def list_conversations(user_id: str, model_id: Optional[str] = None, mode: Optional[str] = None):
    """List conversations for a user, filtered by product and mode"""
    try:
        conversations = db.list_conversations(user_id=user_id, model_id=model_id, mode=mode)
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-room")
async def analyze_room(file: UploadFile = File(...)):
    """
    Analyze uploaded room image for product placement and color matching
    """
    try:
        # Read image data
        image_data = await file.read()
        
        # Analyze room
        analysis_result = await room_analyzer.analyze_room_image(image_data)
        
        if analysis_result["status"] == "error":
            raise HTTPException(status_code=400, detail=analysis_result.get("message"))
        
        return RoomAnalysisResponse(
            status=analysis_result["status"],
            analysis=analysis_result["analysis"],
            confidence=analysis_result["confidence"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/color-match")
async def color_match(
    room_analysis: str,
    product_id: str
):
    """
    Recommend color variant based on room analysis
    """
    try:
        # Get color variants
        variants = product_db.get_color_variants(product_id)
        
        if not variants:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get color recommendation
        recommendation = await room_analyzer.recommend_color_match(
            room_analysis=room_analysis,
            available_colors=variants
        )
        
        return recommendation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess-fit")
async def assess_fit(
    room_analysis: str,
    model_id: str
):
    """
    Assess if product will fit in the room
    """
    try:
        result = product_db.get_model_by_id(model_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Model not found")
        
        product, model = result
        dimensions = model.get('dimensions_cm', [])
        
        assessment = await room_analyzer.assess_product_fit(
            room_analysis=room_analysis,
            product_dimensions=dimensions,
            product_category=product.get('category')
        )
        
        return assessment
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/error-code")
async def lookup_error_code(query: ErrorCodeQuery):
    """
    Look up and explain error codes for the current product
    """
    try:
        # For single-product agent, ensure product is set
        if isinstance(agent, SingleProductAgent):
            if query.model_id != agent.model_id:
                # Update to the requested model
                result = product_db.get_model_by_id(query.model_id)
                if result:
                    product_data, model_data = result
                    agent.update_product(product_data, model_data)
            
            response = await agent.handle_error_code(query.error_code)
        else:
            response = await agent.handle_error_code(
                model_id=query.model_id,
                error_code=query.error_code
            )
        
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend")
async def recommend_products(query: ProductQuery):
    """
    Recommend products based on requirements
    """
    try:
        response = await agent.recommend_products(
            category=query.category,
            requirements=query.requirements or {}
        )
        
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mode")
async def switch_mode(mode_switch: ModeSwitch):
    """
    Switch between PRE_PURCHASE and POST_PURCHASE modes
    """
    try:
        agent.switch_mode(mode_switch.mode)
        return {
            "status": "success",
            "mode": agent.mode,
            "message": f"Switched to {agent.mode} mode"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products")
async def get_products(category: Optional[str] = None):
    """
    Get product catalog
    """
    try:
        if category:
            products = product_db.get_category_products(category)
        else:
            products = {
                "categories": product_db.get_all_categories(),
                "all_products": product_db.products
            }
        
        return products
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/{model_id}")
async def get_model_details(model_id: str):
    """
    Get detailed information about a specific model
    """
    try:
        result = product_db.get_model_by_id(model_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Model not found")
        
        product, model = result
        
        return {
            "product": product,
            "model": model,
            "installation": product_db.get_installation_info(model_id),
            "maintenance": product_db.get_maintenance_info(model_id),
            "warranty_years": product_db.get_warranty_info(model_id)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_conversation():
    """Reset conversation history"""
    agent.reset_conversation()
    return {"status": "success", "message": "Conversation reset"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
