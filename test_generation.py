import asyncio
import os
from dotenv import load_dotenv
# We need to mock the app or run it. 
# For simplicity, I'll import the generate_ui function logic or just run a request against the running server if I were to start it.
# But since I can't easily start a background server and query it in the same script without complexity,
# I will just instantiate the components and run the logic directly.

load_dotenv()

from generative_ui.llm.gemini_client import GeminiClient
from generative_ui.processors.pipeline import PostProcessorPipeline
from generative_ui.prompts.system_prompt import FULL_SYSTEM_PROMPT
from datetime import datetime

async def test_generation():
    print("Testing Generative UI System...")
    
    gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not gemini_key:
        print("Skipping test: No API key found.")
        return

    llm_client = GeminiClient(api_key=gemini_key)
    post_processor = PostProcessorPipeline()
    
    prompt = "What is the time in Tokyo?"
    print(f"Prompt: {prompt}")
    
    system_prompt = FULL_SYSTEM_PROMPT.format(
        current_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        user_location="Unknown"
    )
    
    full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"
    
    print("Generating...")
    try:
        raw_response = llm_client.generate(full_prompt)
        html = llm_client.extract_html(raw_response)
        
        if html:
            final_html = post_processor.process(html)
            print("Success! Generated HTML length:", len(final_html))
            print("Snippet:", final_html[:200])
            
            # Save to file for inspection
            with open("test_output.html", "w") as f:
                f.write(final_html)
            print("Saved to test_output.html")
        else:
            print("Failed to extract HTML.")
            print("Raw response:", raw_response[:500])
            
    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    asyncio.run(test_generation())
