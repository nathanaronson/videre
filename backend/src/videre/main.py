from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from .integration import integrate

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
        transcript = await integrate(payload.topic)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))