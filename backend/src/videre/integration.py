# from dotenv import load_dotenv
# from .claude_client import run_claude_completion, ClaudeError

# load_dotenv()

# async def refine_query(user_prompt: str) -> str:
#     """Receive user prompt, create refined 'better' query from Claude for transcript."""

#     try:
#         prompt = f"""
#         You are an expert educational content designer. Given this user query: "{user_prompt}",

#         Rewrite it into a comprehensive and structured prompt suitable for a large language model to generate an educational video script.
#         The refined prompt should include:

#         - Clear definitions of key terms and concepts.
#         - A breakdown of major subtopics or sections.
#         - Step-by-step explanations of processes, mechanisms, or procedures.
#         - Examples, analogies, or visualizations that make concepts easier to understand.
#         - A logical flow that a beginner could follow.

#         The final output should be a detailed, beginner-friendly instructional prompt that fully guides an AI to teach this topic in a concise yet thorough way.
#         """

#         result_text = await run_claude_completion(
#             prompt=prompt,
#             model="claude-sonnet-4-5-20250929",
#             temperature=0.7,
#             max_tokens=500,
#         )

#         if not result_text:
#             raise Exception("No output received from the model")

#         return result_text
#     except ClaudeError as ce:
#         print(f"\nClaude error in refine_query: {str(ce)}")
#         return user_prompt
#     except Exception as e:
#         print(f"\nError in refine_query: {str(e)}")
#         return user_prompt


# async def create_transcript(transcript_prompt: str) -> str:
#     """Receive LLM refined user prompt, create transcript for an educational video."""

#     try:
#         prompt = f"""
#         You are now an educational video scriptwriter. Using this refined query: "{transcript_prompt}",

#         Generate a line-by-line transcript suitable for a 60-second educational video. Follow these rules:

#         - Write only the words that will be spoken (do not include timestamps or stage directions).
#         - Introduce the topic clearly in the first few lines.
#         - Cover key concepts, definitions, subtopics
#         - Move on to step-by-step explanations in a simple, beginner-friendly language.
#         - Include examples or analogies where appropriate to clarify difficult concepts.
#         - Ensure a smooth, logical flow that is easy for a learner to follow in under a minute.
#         - Keep sentences concise and engaging, as if speaking to a live audience.

#         The output should be ready to use as a spoken educational transcript.
#         """

#         result_text = await run_claude_completion(
#             prompt=prompt,
#             model="claude-sonnet-4-5-20250929",
#             temperature=0.7,
#             max_tokens=500,
#         )

#         if not result_text:
#             raise Exception("No output received from the model")

#         return result_text
#     except ClaudeError as ce:
#         print(f"\nClaude error in create_transcript: {str(ce)}")
#         return f"Unable to create transcript for: {transcript_prompt}"
#     except Exception as e:
#         print(f"\nError in create_transcript: {str(e)}")
#         return f"Unable to create transcript for: {transcript_prompt}"


# async def integrate(user_prompt: str):
#     """Main integration function that processes a user prompt to create an educational video."""
#     print("1. Refining your query...")
#     refined_prompt = await refine_query(user_prompt)
#     print("\nRefined prompt:", refined_prompt)

#     print("\n2. Creating educational transcript...")
#     transcript = await create_transcript(refined_prompt)
#     print("\nGenerated transcript:", transcript)

#     return transcript
