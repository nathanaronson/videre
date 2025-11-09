# backend/src/videre/utils/fetch_context7_docs.py
import aiohttp
import os

CONTEXT7_API_URL = "https://context7.com/api/v1"
CONTEXT7_API_KEY = os.getenv("CONTEXT7_API_KEY")

async def fetch_context7_docs(topic: str = "manim-voiceover") -> str:
    """
    Fetch live docs from Context7 API for a given topic.
    Returns the documentation as plain text.
    """
    headers = {
        "Authorization": f"Bearer {CONTEXT7_API_KEY}"
    }
    
    url = f"{CONTEXT7_API_URL}/vercel/next.js"  # We'll dynamically construct below
    
    # Context7 API expects query params: type (txt/json), topic, tokens
    params = {
        "type": "txt",          # Return as plain text
        "topic": topic,         # Search topic
        "tokens": 5000          # Max tokens to fetch
    }
    
    library = "manimcommunity/manim-voiceover"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{CONTEXT7_API_URL}/{library}",
            headers={"Authorization": f"Bearer {CONTEXT7_API_KEY}"},
            params={"type": "txt", "topic": topic, "tokens": 5000},
        ) as response:
            if response.status != 200:
                raise Exception(f"Context7 API error: {response.status} {await response.text()}")
            return await response.text()

