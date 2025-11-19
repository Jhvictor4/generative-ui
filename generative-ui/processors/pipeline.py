import os
import re
from bs4 import BeautifulSoup

class PostProcessorPipeline:
    def __init__(self):
        self.processors = [
            self.inject_api_keys,
            self.fix_javascript_errors,
            self.fix_css_issues,
            self.validate_html_structure,
            # self.fix_image_sources, # Not implemented yet
            # self.remove_hallucinated_assets # Not implemented yet
        ]

    def process(self, html: str) -> str:
        for processor in self.processors:
            html = processor(html)
        return html

    def inject_api_keys(self, html: str) -> str:
        """Replace API key placeholders with actual keys"""
        replacements = {
            'YOUR_GOOGLE_MAPS_API_KEY': os.environ.get('GOOGLE_MAPS_KEY', ''),
            'YOUR_API_KEY_HERE': os.environ.get('GOOGLE_API_KEY', '')
        }

        for placeholder, key in replacements.items():
            if key:
                html = html.replace(placeholder, key)

        return html

    def fix_javascript_errors(self, html: str) -> str:
        """Fix common JS parsing issues"""
        # Fix unclosed template literals
        html = re.sub(r'`([^`]*?)$', r'`\1`', html, flags=re.MULTILINE)

        # Fix missing semicolons before try blocks
        html = re.sub(r'(\w)\s*\ntry\s*{', r'\1;\ntry {', html)

        # Fix arrow functions with incorrect syntax
        html = re.sub(r'=>\s*{\s*}', r'=> { return null; }', html)

        return html

    def fix_css_issues(self, html: str) -> str:
        """Fix Tailwind CSS issues"""
        # Remove circular dependencies (simple heuristic)
        html = re.sub(r'class="([^"]*)\1+"', r'class="\1"', html)

        # Fix malformed Tailwind classes
        html = re.sub(r'class="[^"]*undefined[^"]*"', 'class=""', html)

        return html

    def validate_html_structure(self, html: str) -> str:
        """Ensure proper HTML structure"""
        soup = BeautifulSoup(html, 'html.parser')

        # Ensure required tags exist
        if not soup.find('head'):
            head = soup.new_tag('head')
            if soup.html:
                soup.html.insert(0, head)
            else:
                # If no html tag, wrap everything in html
                new_html = soup.new_tag('html')
                new_html.append(head)
                new_html.append(soup)
                soup = new_html

        if not soup.find('body'):
            body = soup.new_tag('body')
            if soup.html:
                soup.html.append(body)

        # Ensure Tailwind is included
        if not soup.find('script', src=lambda x: x and 'tailwindcss' in x):
            script = soup.new_tag('script', src='https://cdn.tailwindcss.com')
            if soup.head:
                soup.head.append(script)

        return str(soup)
