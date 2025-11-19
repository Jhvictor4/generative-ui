import os
import aiohttp
from fastapi import APIRouter, Query, HTTPException

router = APIRouter()

@router.get("/")
async def search_image(query: str = Query(..., description="Image search query")):
    """
    Image search endpoint
    Returns: Thumbnail URLs for the query
    """
    api_key = os.environ.get('GOOGLE_API_KEY')
    cx = os.environ.get('GOOGLE_IMAGE_CX') or os.environ.get('GOOGLE_CX') # Fallback to main CX if image specific not provided

    if not api_key or not cx:
         # Fallback to placeholder if keys missing
         # For demo purposes, return some placeholder images from unsplash or similar if we can't search
         # But better to raise error or return empty to force user to provide keys for "Real" experience
         # I'll try to search, if fails, return empty list
         pass

    if api_key and cx:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cx,
            'q': query,
            'searchType': 'image',
            'num': 5,
            'imgSize': 'medium'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        thumbnails = []
                        for item in data.get('items', []):
                            thumbnails.append(item['image']['thumbnailLink'])
                        return {'thumbnails': thumbnails}
        except Exception:
            pass
            
    # Fallback if search fails or no keys
    return {'thumbnails': []}
