import asyncio
from dotenv import load_dotenv
from integration import integrate

load_dotenv()

def createPromptToSpeech(prompt: str) -> str:
    """Receive LLM prompt transcript to create speech from ElevenLabs."""

    return None

async def main():
    print("Welcome to Videre - Educational Video Generator")
    print("What would you like to learn about today?")
    user_prompt = input("> ")
    
    print("\nGenerating educational video content...")
    try:
        result = await integrate(user_prompt)
        print("\nProcess completed successfully!")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())