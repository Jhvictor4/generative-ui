import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from generative_ui.llm.gemini_client import GeminiClient
from generative_ui.processors.pipeline import PostProcessorPipeline
from generative_ui.prompts.system_prompt import FULL_SYSTEM_PROMPT
from generative_ui.tools import search, image_gen, image_search, maps

app = FastAPI(title="Generative UI System")

# Add CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount tool endpoints
app.include_router(search.router, prefix="/search", tags=["tools"])
app.include_router(image_gen.router, prefix="/gen", tags=["tools"])
app.include_router(image_search.router, prefix="/image", tags=["tools"])
app.include_router(maps.router, prefix="/maps", tags=["tools"])

# Initialize components
# Use a default key if not set, but it will fail if not provided eventually
gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if not gemini_key:
    print("WARNING: GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables.")

llm_client = GeminiClient(api_key=gemini_key) if gemini_key else None
post_processor = PostProcessorPipeline()

class GenerateRequest(BaseModel):
    prompt: str
    style: str = "default"

@app.post("/generate")
async def generate_ui(request: GenerateRequest):
    """
    Main endpoint to generate UI from prompt
    """
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not initialized. Check API keys.")

    try:
        # 1. Prepare system prompt with context
        # For simplicity, we use a fixed location or "Unknown"
        system_prompt = FULL_SYSTEM_PROMPT.format(
            current_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            user_location="Unknown" 
        )

        # 2. Combine system and user prompts
        full_prompt = f"{system_prompt}\n\nUser Request: {request.prompt}"

        # 3. Generate HTML via LLM
        raw_response = llm_client.generate(full_prompt)

        # 4. Extract HTML from markers
        html = llm_client.extract_html(raw_response)

        if not html:
            # If extraction failed, maybe the model just outputted code without markers
            # We can return the raw response if it looks like HTML, or error
            if "<html" in raw_response:
                html = raw_response
            else:
                raise ValueError("No valid HTML found in response")

        # 5. Post-process
        final_html = post_processor.process(html)

        return {
            'success': True,
            'html': final_html
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {'status': 'healthy'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
