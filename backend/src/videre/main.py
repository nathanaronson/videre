import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# from .integration import integrate
from .database import close_db, connect_db, get_database
from .models import ChatHistory, ChatHistoryListResponse, ChatHistoryResponse, ChatMessage
from .utils.create_video import generate_video_with_gtts
from .utils.send_to_aws import create_presigned_url, upload_file_to_s3

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_db()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_db()

class TopicPayload(BaseModel):
    topic: str

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}

async def _emit_event(event_type: str, data: dict):
    """Helper function to format SSE events"""
    event_data = json.dumps({"type": event_type, **data})
    return f"data: {event_data}\n\n"

@app.post("/api/integrate")
async def integrate_endpoint(payload: TopicPayload):
    """Accept a JSON payload { topic: str } and stream video generation progress via SSE.

    This endpoint streams the following events:
    - video_generation_start: Video generation has started
    - video_generation_complete: Video generation has completed
    - saving_start: Starting to save/upload video to S3
    - saving_complete: Video has been saved/uploaded to S3
    - complete: Final completion with video_id
    """
    async def event_stream():
        try:
            print(payload)

            # Create initial chat history entry
            db = get_database()
            chat_entry = {
                "topic": payload.topic,
                "chat_messages": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            chat_result = await db.chat_histories.insert_one(chat_entry)
            chat_id = str(chat_result.inserted_id)

            # Queue to stream events in real-time
            event_queue = asyncio.Queue()

            # Event callback function to put events in the queue
            async def emit_status(event_type: str, data: dict):
                event_str = await _emit_event(event_type, data)
                await event_queue.put(event_str)
                # Add a small delay to ensure the event is processed
                await asyncio.sleep(0)

            # Start video generation
            yield await _emit_event("video_generation_start", {"message": "Starting video generation..."})

            # Generate video with event callback (run in background)
            async def generate_task():
                return await generate_video_with_gtts(payload.topic, emit_status)

            generation_task = asyncio.create_task(generate_task())

            # Yield events as they come in while generation is running
            while not generation_task.done():
                try:
                    # Wait for events with a short timeout
                    event = await asyncio.wait_for(event_queue.get(), timeout=0.5)
                    yield event
                except asyncio.TimeoutError:
                    # Send a heartbeat comment to keep connection alive
                    yield ": heartbeat\n\n"
                    continue

            # Get the result
            result = await generation_task

            # Yield any remaining events
            while not event_queue.empty():
                event = await event_queue.get()
                yield event
            
            if not result or result[0] is None or result[1] is None:
                yield await _emit_event("error", {"message": "Failed to generate video - no valid result returned"})
                return
            
            video_uuid, scene_class_name = result
            
            yield await _emit_event("video_generation_complete", {"message": "Video generated successfully."})
            
            # Manim saves the video relative to project_root where it's run from
            # Path: project_root / "media" / "videos" / "generated_scene" / "1080p60" / f"{scene_class_name}.mp4"
            project_root = Path(__file__).parent.parent
            video_path = project_root / "media" / "videos" / "generated_scene" / "1080p60" / f"{scene_class_name}.mp4"
            
            if not video_path.exists():
                yield await _emit_event("error", {"message": f"Video file not found at {video_path}"})
                return
            
            # Start saving/uploading to S3
            yield await _emit_event("saving_start", {"message": "Uploading video to S3..."})
            
            upload_file_to_s3(str(video_path), video_uuid)
            
            yield await _emit_event("saving_complete", {"message": "Video uploaded to AWS successfully."})
            
            # Construct the S3 URL
            bucket_name = os.getenv("AWS_MP4_S3_BUCKET_ID", "videre-s3")
            aws_region = os.getenv("AWS_REGION", "us-east-1")

            video_url = create_presigned_url(video_uuid)
            print(video_url)

            yield await _emit_event("url_created", {"message": "Presigned URL created successfully."})

            # Update chat history with video information
            await db.chat_histories.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$set": {
                        "video_url": video_url,
                        "video_id": video_uuid,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            # Final completion event with video_id and chat_id
            yield await _emit_event("complete", {
                "success": True,
                "video_id": video_uuid,
                "video_url": video_url,
                "chat_id": chat_id
            })

        except Exception as e:
            yield await _emit_event("error", {"message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@app.post("/api/chat-history", response_model=ChatHistoryResponse)
async def create_chat_history(chat: ChatHistory):
    """Create a new chat history entry."""
    db = get_database()
    chat_dict = chat.model_dump(exclude={"id"})
    chat_dict["created_at"] = datetime.utcnow()
    chat_dict["updated_at"] = datetime.utcnow()

    result = await db.chat_histories.insert_one(chat_dict)
    chat_dict["_id"] = str(result.inserted_id)

    return ChatHistoryResponse(
        id=str(result.inserted_id),
        topic=chat_dict["topic"],
        video_url=chat_dict.get("video_url"),
        video_id=chat_dict.get("video_id"),
        created_at=chat_dict["created_at"],
        updated_at=chat_dict["updated_at"],
        chat_messages=chat_dict.get("chat_messages", [])
    )


@app.get("/api/chat-history", response_model=ChatHistoryListResponse)
async def get_chat_histories(skip: int = 0, limit: int = 50):
    """Get all chat histories with pagination."""
    db = get_database()

    # Get total count
    total = await db.chat_histories.count_documents({})

    # Get paginated results, sorted by most recent first
    cursor = db.chat_histories.find().sort("created_at", -1).skip(skip).limit(limit)
    chats = []

    async for doc in cursor:
        chats.append(ChatHistoryResponse(
            id=str(doc["_id"]),
            topic=doc["topic"],
            video_url=doc.get("video_url"),
            video_id=doc.get("video_id"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            chat_messages=doc.get("chat_messages", [])
        ))

    return ChatHistoryListResponse(total=total, chats=chats)


@app.get("/api/chat-history/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(chat_id: str):
    """Get a specific chat history by ID."""
    db = get_database()

    try:
        doc = await db.chat_histories.find_one({"_id": ObjectId(chat_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid chat ID format")

    if not doc:
        raise HTTPException(status_code=404, detail="Chat history not found")

    return ChatHistoryResponse(
        id=str(doc["_id"]),
        topic=doc["topic"],
        video_url=doc.get("video_url"),
        video_id=doc.get("video_id"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        chat_messages=doc.get("chat_messages", [])
    )


@app.put("/api/chat-history/{chat_id}", response_model=ChatHistoryResponse)
async def update_chat_history(chat_id: str, chat: ChatHistory):
    """Update an existing chat history."""
    db = get_database()

    try:
        chat_dict = chat.model_dump(exclude={"id"})
        chat_dict["updated_at"] = datetime.utcnow()

        result = await db.chat_histories.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": chat_dict}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Chat history not found")

        updated_doc = await db.chat_histories.find_one({"_id": ObjectId(chat_id)})

        return ChatHistoryResponse(
            id=str(updated_doc["_id"]),
            topic=updated_doc["topic"],
            video_url=updated_doc.get("video_url"),
            video_id=updated_doc.get("video_id"),
            created_at=updated_doc["created_at"],
            updated_at=updated_doc["updated_at"],
            chat_messages=updated_doc.get("chat_messages", [])
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/chat-history/{chat_id}")
async def delete_chat_history(chat_id: str):
    """Delete a chat history by ID."""
    db = get_database()

    try:
        result = await db.chat_histories.delete_one({"_id": ObjectId(chat_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Chat history not found")

        return {"message": "Chat history deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
