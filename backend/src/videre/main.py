import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# from .integration import integrate
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
            
            # Queue to stream events in real-time
            event_queue = asyncio.Queue()
            
            # Event callback function to put events in the queue
            async def emit_status(event_type: str, data: dict):
                event_str = await _emit_event(event_type, data)
                await event_queue.put(event_str)
            
            # Start video generation
            yield await _emit_event("video_generation_start", {"message": "Starting video generation..."})
            
            # Generate video with event callback (run in background)
            async def generate_task():
                return await generate_video_with_gtts(payload.topic, emit_status)
            
            generation_task = asyncio.create_task(generate_task())
            
            # Yield events as they come in while generation is running
            while not generation_task.done():
                try:
                    event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                    yield event
                except asyncio.TimeoutError:
                    # Check if task is still running
                    if generation_task.done():
                        break
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
            
            # Final completion event with video_id
            yield await _emit_event("complete", {
                "success": True,
                "video_id": video_uuid,
                "video_url": video_url
            })
            
        except Exception as e:
            yield await _emit_event("error", {"message": str(e)})
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
