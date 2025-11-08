from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from .integration import integrate

load_dotenv()

app = FastAPI(title="Videre API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TopicPayload(BaseModel):
    topic: str


@app.post("/api/integrate")
async def integrate_endpoint(payload: TopicPayload):
    """Accept a JSON payload { topic: str } and return the generated transcript.

    This endpoint calls the async `integrate` function from the local package
    and returns the transcript.
    """
    try:
        transcript = await integrate(payload.topic)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health():
    return {"status": "ok"}


async def main():
    print("Welcome to Videre - Educational Video Generator")
    print("What would you like to learn about today?")
    user_prompt = input("> ")
    
    print("\nGenerating educational video content...")
    try:
        result = await integrate(user_prompt)
        print("\nProcess completed successfully!")
        print(result)
    except Exception as e:
        print(f"\nError occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())