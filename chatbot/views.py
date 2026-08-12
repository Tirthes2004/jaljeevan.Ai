# chatbot/views.py
import os
import json
import numpy as np
import requests
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# ================================
# CHATBOT CONFIGURATION
# ================================

GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', 'your-api-key-here')
FAISS_INDEX_FILE = os.path.join(settings.BASE_DIR, "faiss_index.bin")
DOCS_META_FILE = os.path.join(settings.BASE_DIR, "docs.json")
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-2.5-flash"

# ================================
# CHATBOT INITIALIZATION
# ================================

index = None
embed_model = None
documents = []
ids = []
metas = []

chatbot_initialized = False
chatbot_initializing = False


def initialize_chatbot():
    """Load FAISS and SentenceTransformer only when chatbot is actually used."""
    global index, embed_model, documents, ids, metas
    global chatbot_initialized, chatbot_initializing

    if chatbot_initialized:
        return True

    if chatbot_initializing:
        return False

    chatbot_initializing = True

    try:
        print("🤖 Initializing chatbot...")

        if not os.path.exists(FAISS_INDEX_FILE):
            print(f"⚠️ FAISS index not found: {FAISS_INDEX_FILE}")
            return False

        if not os.path.exists(DOCS_META_FILE):
            print(f"⚠️ Documents metadata not found: {DOCS_META_FILE}")
            return False

        import faiss
        from sentence_transformers import SentenceTransformer

        print("📚 Loading FAISS index...")
        index = faiss.read_index(FAISS_INDEX_FILE)

        print("📄 Loading documents...")
        with open(DOCS_META_FILE, "r", encoding="utf-8") as f:
            meta_data = json.load(f)

        documents = meta_data["documents"]
        ids = meta_data["ids"]
        metas = meta_data["metas"]

        print("🧠 Loading embedding model...")
        embed_model = SentenceTransformer(
            EMBED_MODEL_NAME,
            device="cpu"
        )

        chatbot_initialized = True
        print("✅ Chatbot initialized successfully!")

        return True

    except Exception as e:
        print(f"⚠️ Chatbot initialization warning: {e}")
        index = None
        embed_model = None
        return False

    finally:
        chatbot_initializing = False
# ================================
# UTILITY FUNCTIONS
# ================================

def retrieve_documents(query: str, k: int = 4):
    """Retrieve relevant documents using FAISS."""

    # Load chatbot only when it is actually needed
    if not initialize_chatbot():
        return []

    if embed_model is None or index is None:
        return []

    try:
        query_emb = embed_model.encode(
            [query],
            convert_to_numpy=True
        )

        query_emb = np.asarray(
            query_emb,
            dtype="float32"
        )

        distances, indices = index.search(query_emb, k)

        results = []

        for idx in indices[0]:
            if idx == -1:
                continue

            results.append({
                "id": ids[idx],
                "text": documents[idx],
                "meta": metas[idx]
            })

        return results

    except Exception as e:
        print(f"Document retrieval error: {e}")
        return []
    
def call_gemini_api(prompt: str) -> str:
    """Call Google Gemini API"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your-api-key-here':
        return "I need a valid Gemini API key to provide intelligent responses. Please configure GEMINI_API_KEY in your environment variables."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "I'm having trouble connecting to my AI knowledge base right now. Please try asking a different question or try again in a moment."

# Import models and utils
try:
    from .models import ChatSession, ChatMessage
except ImportError:
    # Handle case where models don't exist yet
    print("⚠️ ChatBot models not found. Please run migrations.")
    ChatSession = None
    ChatMessage = None

try:
    from .utils import harvest_water_cubic_meters, recommend_tank_size, plausible_check
except ImportError:
    # Fallback functions if utils don't exist
    def harvest_water_cubic_meters(roof_area_m2: float, annual_rainfall_mm: float, runoff_coeff: float) -> float:
        rainfall_m = annual_rainfall_mm / 1000.0
        return roof_area_m2 * rainfall_m * runoff_coeff
    
    def recommend_tank_size(roof_area_m2: float, annual_rainfall_mm: float, runoff_coeff: float, storage_months: int = 2) -> float:
        annual_harvest = harvest_water_cubic_meters(roof_area_m2, annual_rainfall_mm, runoff_coeff)
        monthly = annual_harvest / 12.0
        return monthly * storage_months
    
    def plausible_check(value: float):
        if value < 0 or value > 1e6:
            raise ValueError(f"Value {value} is outside plausible range")
        return True

# ================================
# DJANGO VIEWS
# ================================

@csrf_exempt
def chat_api(request):
    """Main chat API endpoint for modal"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Extract optional calculation parameters
        roof_area = data.get('roof_area')
        annual_rainfall = data.get('annual_rainfall') 
        runoff = data.get('runoff', 0.8)
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Message is required'})
        
        # Handle calculations if parameters provided
        if roof_area and annual_rainfall:
            try:
                plausible_check(roof_area)
                plausible_check(annual_rainfall)
                
                water_volume = harvest_water_cubic_meters(roof_area, annual_rainfall, runoff)
                tank_size = recommend_tank_size(roof_area, annual_rainfall, runoff, storage_months=2)
                
                bot_response = (
                    f"💧 **Calculation Results**\n\n"
                    f"**Your Inputs:**\n"
                    f"• Roof Area: {roof_area} m²\n"
                    f"• Annual Rainfall: {annual_rainfall} mm\n"
                    f"• Runoff Coefficient: {runoff}\n\n"
                    f"**Harvesting Potential:**\n"
                    f"• Annual Water: **{water_volume:.1f} m³** ({water_volume * 1000:.0f} liters)\n"
                    f"• Recommended Tank: **{tank_size:.1f} m³** ({tank_size * 1000:.0f} liters)\n\n"
                    f"💡 This tank size provides 2 months of storage capacity."
                )
                
                response_type = 'calculation'
                sources = []
                
            except ValueError as e:
                bot_response = f"⚠️ Calculation Error: {str(e)}. Please check your inputs."
                response_type = 'error'
                sources = []
        
        else:
            # AI-powered response
            try:
                # Try to retrieve documents
                docs = retrieve_documents(user_message, k=4)
                
                if docs:
                    # Use AI with retrieved context
                    context = "\n\n".join([f"[{d['id']}] {d['text']}" for d in docs])
                    system_prompt = (
                        "You are JalJeevan.AI Assistant named Isha , an expert in rainwater harvesting and water conservation.\n\n"
                        "Provide helpful, accurate, and actionable advice about:\n"
                        "- Rainwater harvesting system design and sizing\n"
                        "- Installation, maintenance, and troubleshooting\n"
                        "- Cost-benefit analysis and ROI calculations\n"
                        "- Government policies, subsidies, and incentives\n"
                        "- Environmental benefits and sustainability\n\n"
                        "Keep responses concise but comprehensive (max 200 words).\n"
                        "--- RULES ---\n"
                        "1. If the user asks about 'this website', 'your features', 'about the site', or 'JalJeevan.ai', you MUST prioritize context from sources that start with 'page_' (e.g., 'page_home', 'page_about').\n"
                        "2. If no 'page_' sources are available, it is OK to say you don't have information about the website.\n"
                        "3. For all other technical questions about RWH, you can use any relevant context.\n"
                        "--- END RULES ---\n\n"
                        f"Context from knowledge base:\n{context}\n\n"
                        f"User Question: {user_message}\n\n"
                        "Response:"
                    )
                    
                    bot_response = call_gemini_api(system_prompt)
                    sources = [d["id"] for d in docs]
                else:
                    # Basic response without AI
                    bot_response = get_basic_response(user_message)
                    sources = []
                
                response_type = 'ai'
                
            except Exception as e:
                print(f"AI response error: {e}")
                bot_response = "I apologize, but I'm experiencing technical difficulties. Please try rephrasing your question or try again in a moment."
                response_type = 'error'
                sources = []
        
        # Save to database if models exist
        if ChatSession and ChatMessage:
            try:
                session, created = ChatSession.objects.get_or_create(
                    session_id=session_id,
                    defaults={'user': request.user if request.user.is_authenticated else None}
                )
                
                ChatMessage.objects.create(
                    session=session,
                    user_message=user_message,
                    bot_response=bot_response,
                    response_type=response_type,
                    sources=sources
                )
            except Exception as e:
                print(f"Database save error: {e}")
        
        return JsonResponse({
            'success': True,
            'response': bot_response,
            'response_type': response_type,
            'sources': sources,
            'session_id': session_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        print(f"Chat API error: {e}")
        return JsonResponse({'success': False, 'error': 'Internal server error'})

def chat_history(request, session_id):
    """Get chat history for a session"""
    if not ChatSession:
        return JsonResponse({'success': False, 'error': 'Database not configured'})
    
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.all()
        
        history = []
        for msg in messages:
            history.append({
                'user_message': msg.user_message,
                'bot_response': msg.bot_response,
                'response_type': msg.response_type,
                'sources': msg.sources,
                'timestamp': msg.timestamp.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'history': history
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session not found'
        })
    except Exception as e:
        print(f"Chat history error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error retrieving chat history'
        })

def get_basic_response(user_message: str) -> str:
    """Provide basic responses when AI is not available"""
    user_message = user_message.lower()
    
    if 'calculator' in user_message or 'calculate' in user_message:
        return ("I can help you calculate rainwater harvesting potential! "
                "Please provide your roof area (in m²) and annual rainfall (in mm). "
                "For example: 'Calculate for 100m² roof with 800mm rainfall'")
    
    elif 'tank' in user_message or 'storage' in user_message:
        return ("For tank sizing, I recommend 2-6 months of storage capacity. "
                "This depends on your usage patterns, rainfall seasonality, and local climate. "
                "A typical household needs 10-20 liters per person per day.")
    
    elif 'cost' in user_message or 'price' in user_message:
        return ("Rainwater harvesting system costs vary by size and complexity:\n"
                "• Basic rooftop system: ₹15,000-50,000\n"
                "• Complete system with filtration: ₹50,000-2,00,000\n"
                "• Payback period: 3-7 years depending on water costs")
    
    elif 'benefit' in user_message:
        return ("Key benefits of rainwater harvesting:\n"
                "• Reduces water bills by 30-50%\n"
                "• Provides backup during water shortages\n"
                "• Reduces groundwater depletion\n"
                "• Improves soil moisture and reduces erosion\n"
                "• Eligible for government subsidies")
    
    elif 'maintenance' in user_message:
        return ("Regular maintenance includes:\n"
                "• Clean gutters and filters monthly\n"
                "• Check first-flush diverters after rain\n"
                "• Inspect tank for algae/sediment quarterly\n"
                "• Service pumps annually\n"
                "• Test water quality if used for drinking")
    
    else:
        return ("I'm here to help with rainwater harvesting questions! "
                "Ask me about system design, calculations, costs, benefits, or maintenance. "
                "For calculations, provide your roof area and local rainfall data.")