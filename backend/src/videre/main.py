from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
# from .integration import integrate
from .utils.create_video import generate_video_with_gtts
from .utils.send_to_aws import upload_file_to_s3

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

@app.post("/api/integrate")
async def integrate_endpoint(payload: TopicPayload):
    """Accept a JSON payload { topic: str } and return the generated transcript.

    This endpoint calls the async `integrate` function from the local package
    and returns the transcript.
    """
    print(payload)
    try:
        result = await generate_video_with_gtts(payload.topic)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate video")
        
        video_uuid, scene_class_name = result
        
        print("Video generated successfully.")

        # Manim saves the video relative to project_root where it's run from
        # Path: project_root / "media" / "videos" / "generated_scene" / "1080p60" / f"{scene_class_name}.mp4"
        project_root = Path(__file__).parent.parent
        video_path = project_root / "media" / "videos" / "generated_scene" / "1080p60" / f"{scene_class_name}.mp4"
        
        if not video_path.exists():
            raise HTTPException(status_code=500, detail=f"Video file not found at {video_path}")
        
        upload_file_to_s3(str(video_path), video_uuid)
        print("Video uploaded to AWS successfully.")
        return {"success": True, "video_id": video_uuid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))