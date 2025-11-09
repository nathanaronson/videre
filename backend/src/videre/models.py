"""Pydantic models for chat history and video data."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message in the conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatHistory(BaseModel):
    """Complete chat history for a video generation session."""
    id: Optional[str] = Field(None, alias="_id")
    topic: str
    video_url: Optional[str] = None
    video_id: Optional[str] = None
    chat_messages: List[ChatMessage] = []
    manim_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    id: str
    topic: str
    video_url: Optional[str] = None
    video_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    chat_messages: List[ChatMessage] = []


class ChatHistoryListResponse(BaseModel):
    """Response model for list of chat histories."""
    total: int
    chats: List[ChatHistoryResponse]
