import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from schemas import Event, BlogPost, ContactMessage, ChatMessage
from database import create_document, get_documents, db

app = FastAPI(title="Kenya Arts & Culture AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    topic: Optional[str] = None


def serialize_docs(docs: List[Dict[str, Any]]):
    """Convert MongoDB docs (ObjectId, datetime) to JSON-serializable"""
    from bson import ObjectId
    from datetime import datetime

    out = []
    for d in docs:
        nd = {}
        for k, v in d.items():
            if isinstance(v, ObjectId):
                nd[k] = str(v)
            elif isinstance(v, datetime):
                nd[k] = v.isoformat()
            else:
                nd[k] = v
        out.append(nd)
    return out


@app.get("/")
def read_root():
    return {"message": "Kenya Arts & Culture AI Agent Backend"}


@app.get("/api/pricing")
def pricing():
    return {
        "currency": "KES",
        "tiers": [
            {"name": "Explorer", "price": 0, "features": ["Browse events", "Read blog", "Basic chat"]},
            {"name": "Creator", "price": 499, "features": ["Event alerts", "Saved favorites", "Priority chat"]},
            {"name": "Patron", "price": 1499, "features": ["VIP presales", "Artist Q&A", "Monthly merch draw"]},
        ]
    }


@app.get("/api/events")
def list_events(category: Optional[str] = None, city: Optional[str] = None, limit: Optional[int] = Query(12, ge=1, le=100)):
    filt: Dict[str, Any] = {}
    if category:
        filt["category"] = category
    if city:
        filt["city"] = city
    docs = get_documents("event", filt, limit)
    return serialize_docs(docs)


@app.post("/api/events")
def create_event(event: Event):
    inserted_id = create_document("event", event)
    return {"id": inserted_id}


@app.get("/api/blogs")
def list_blogs(limit: Optional[int] = Query(6, ge=1, le=50)):
    docs = get_documents("blogpost", {}, limit)
    return serialize_docs(docs)


@app.post("/api/blogs")
def create_blog(post: BlogPost):
    inserted_id = create_document("blogpost", post)
    return {"id": inserted_id}


@app.post("/api/contact")
def submit_contact(msg: ContactMessage):
    inserted_id = create_document("contactmessage", msg)
    return {"status": "ok", "id": inserted_id}


@app.post("/api/chat")
def chat(req: ChatRequest):
    # Save user message
    create_document("chatmessage", ChatMessage(role="user", text=req.message, topic=req.topic or "general"))

    text = req.message.lower()
    reply = "Niaje! I can help you discover Kenya's arts, music, culture, history and events. Ask for events in your city, trending artists, or museum tips."

    # Simple intent-based responses
    if any(k in text for k in ["event", "concert", "show", "festival", "gig"]):
        # suggest latest events if available
        try:
            events = serialize_docs(get_documents("event", {}, 3))
        except Exception:
            events = []
        if events:
            lines = [f"- {e.get('title')} • {e.get('city')} • {e.get('date')}" for e in events]
            reply = "Here are a few upcoming picks:\n" + "\n".join(lines)
        else:
            reply = "Tell me your city and genre, and I’ll suggest events (e.g., 'events in Nairobi this weekend')."
    elif any(k in text for k in ["history", "heritage", "maasai", "swahili", "museum"]):
        reply = "Kenya's heritage is rich: explore the National Museum in Nairobi, Fort Jesus in Mombasa (UNESCO), and the Lamu Old Town for Swahili culture."
    elif any(k in text for k in ["music", "artist", "band", "genge", "benga", "afro"]):
        reply = "For Kenyan sounds, check out genge, benga, and contemporary afro-fusion. Want recommendations by mood or city?"

    # Save assistant reply
    create_document("chatmessage", ChatMessage(role="assistant", text=reply, topic=req.topic or "general"))

    return {"reply": reply}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
