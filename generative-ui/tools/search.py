import os
import aiohttp
from fastapi import APIRouter, Query, HTTPException

router = APIRouter()

@router.get("/")
async def web_search(query: str = Query(..., description="Search query")):
    """
    Web search endpoint wrapping Google Search API
    Returns: JSON with search results
    """
    api_key = os.environ.get('GOOGLE_API_KEY')
    cx = os.environ.get('GOOGLE_CX')
    
    if not api_key or not cx:
        # Fallback or error if keys are missing. 
        # For reproduction purposes, we might want to mock if keys are missing, 
        # but the whitepaper insists on real data.
        # I'll return a helpful error.
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY or GOOGLE_CX not set")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cx,
        'q': query,
        'num': 10
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=f"Search API error: {error_text}")
                data = await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Format results for LLM consumption
    results = []
    for item in data.get('items', []):
        results.append({
            'title': item.get('title'),
            'snippet': item.get('snippet'),
            'link': item.get('link')
        })

    return {'results': results}
