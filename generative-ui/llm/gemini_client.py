import google.generativeai as genai
from typing import Optional
import os
import re

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Try to use gemini-2.0-flash-exp or gemini-1.5-pro if available
        # The whitepaper recommends Gemini 3 or 2.5 Pro, but we use what's available.
        self.model_name = 'gemini-2.0-flash-exp' 
        try:
            self.model = genai.GenerativeModel(self.model_name)
        except:
            self.model_name = 'gemini-1.5-pro-latest'
            self.model = genai.GenerativeModel(self.model_name)

    def generate(self,
                prompt: str,
                temperature: float = 0.7,
                max_tokens: int = 8000) -> str:
        """
        Generate HTML output from prompt
        """
        generation_config = {
            'temperature': temperature,
            'max_output_tokens': max_tokens,
            'top_p': 0.95,
            'top_k': 40
        }

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            # Fallback or error handling
            print(f"Generation error: {e}")
            raise e

    def extract_html(self, response: str) -> Optional[str]:
        """
        Extract HTML from response markers
        """
        # Look for HTML between markers
        pattern = r'```html\s*(<!DOCTYPE.*?</html>)\s*```'
        match = re.search(pattern, response, re.DOTALL)

        if match:
            return match.group(1)
        
        # Fallback: try to find just the doctype and html tag if markers are missing
        if '<!DOCTYPE html>' in response:
            start = response.find('<!DOCTYPE html>')
            end = response.rfind('</html>') + 7
            if start != -1 and end != -1:
                return response[start:end]

        return None
