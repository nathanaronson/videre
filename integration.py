from dotenv import load_dotenv
from claude_client import run_claude_completion, ClaudeError

load_dotenv()

async def refine_query(user_prompt: str) -> str:
    """Receive user prompt, create refined 'better' query from Claude for transcript."""

    try:
        prompt = f"""
        Given this query: "{user_prompt}",
        Rewrite the query into a detailed educational prompt suitable for an LLM to teach a beginner.
        Include definitions, key subtopics, processes, and concepts the LLM should cover when teaching.
        Make the final prompt clear, complete, and beginner-friendly.
        """

        result_text = await run_claude_completion(
            prompt=prompt,
            model="claude-sonnet-4-5-20250929",
            temperature=0.7,
            max_tokens=500,
        )

        if not result_text:
            raise Exception("No output received from the model")

        return result_text
    except ClaudeError as ce:
        print(f"\nClaude error in refine_query: {str(ce)}")
        return user_prompt
    except Exception as e:
        print(f"\nError in refine_query: {str(e)}")
        return user_prompt


async def create_transcript(transcript_prompt: str) -> str:
    """Receive LLM refined user prompt, create transcript for an educational video."""

    try:
        prompt = f"""
        Given this query: "{transcript_prompt}",
        Create a line-by-line transcript for an educational video lasting at most 30 seconds 
        with only words that will be spoken (no timestamps) by covering key concepts and procedures.
        """

        result_text = await run_claude_completion(
            prompt=prompt,
            model="claude-sonnet-4-5-20250929",
            temperature=0.7,
            max_tokens=500,
        )

        if not result_text:
            raise Exception("No output received from the model")

        return result_text
    except ClaudeError as ce:
        print(f"\nClaude error in create_transcript: {str(ce)}")
        return f"Unable to create transcript for: {transcript_prompt}"
    except Exception as e:
        print(f"\nError in create_transcript: {str(e)}")
        return f"Unable to create transcript for: {transcript_prompt}"


async def integrate(user_prompt: str):
    """Main integration function that processes a user prompt to create an educational video."""
    print("1. Refining your query...")
    refined_prompt = await refine_query(user_prompt)
    print("\nRefined prompt:", refined_prompt)

    print("\n2. Creating educational transcript...")
    transcript = await create_transcript(refined_prompt)
    print("\nGenerated transcript:", transcript)

    return transcript
