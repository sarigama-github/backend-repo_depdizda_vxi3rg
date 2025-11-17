"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Core domain schemas for the Kenyan Arts & Culture app

class Event(BaseModel):
    """
    Events collection schema
    Collection name: "event"
    """
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Short description")
    category: str = Field(..., description="music | art | culture | history | dance | film | festival")
    city: str = Field(..., description="City or town in Kenya")
    venue: Optional[str] = Field(None, description="Venue name")
    date: str = Field(..., description="ISO date string e.g., 2025-12-01")
    price: Optional[float] = Field(None, ge=0, description="Ticket price in KES")
    image_url: Optional[str] = Field(None, description="Cover image URL")

class BlogPost(BaseModel):
    """
    Blog posts about arts, culture, music, and history
    Collection name: "blogpost"
    """
    title: str
    excerpt: Optional[str] = None
    content: str
    author: str = Field(..., description="Author name")
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

class ContactMessage(BaseModel):
    """
    Contact form submissions
    Collection name: "contactmessage"
    """
    name: str
    email: str
    message: str

class ChatMessage(BaseModel):
    """
    Saved chat messages for the assistant
    Collection name: "chatmessage"
    """
    role: str = Field(..., description="user | assistant")
    text: str
    topic: Optional[str] = Field(None, description="Optional topic tag")

# Example schemas kept for reference
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
