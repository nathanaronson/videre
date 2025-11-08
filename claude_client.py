"""A minimal async client wrapper for Anthropic/Claude using the official SDK.

This module provides `run_claude_completion` which uses the Anthropic Python SDK
to interact with Claude's API.

Environment variables supported:
- CLAUDE_API_KEY (required)
"""
import os
from dotenv import load_dotenv
import anthropic
import asyncio
from functools import partial

load_dotenv()

# Get API key from environment
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

class ClaudeError(RuntimeError):
    pass

async def run_claude_completion(
    prompt: str,
    model="claude-sonnet-4-5-20250929",
    max_tokens: int = 500,
    temperature: float = 0.7,
) -> str:
    """Run a completion using the Anthropic Claude API and return the text output.
    
    Uses the official Anthropic Python SDK for reliable API interaction.
    Available models: claude-sonnet-4-5-20250929
    """
    if not CLAUDE_API_KEY:
        raise ClaudeError("No API key found. Set CLAUDE_API_KEY in the environment")

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            partial(
                client.messages.create,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
        )
        return response.content[0].text
    except Exception as e:
        raise ClaudeError(f"Claude request failed: {str(e)}")
