"""URL fetching and conversion to markdown."""

import re
from urllib.parse import urljoin, urlparse
from typing import Optional

import requests
from bs4 import BeautifulSoup


class URLFetcher:
    """Fetch web pages and convert to markdown."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "lsearch/0.1.0 (Documentation Fetcher)"
        })

    def fetch(self, url: str) -> str:
        """Fetch a URL and return markdown content."""
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        # Determine content type
        content_type = response.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            # Handle JSON (e.g., Swagger/OpenAPI)
            return self._convert_json_to_md(response.text, url)
        else:
            # HTML
            return self._convert_html_to_md(response.text, url)

    def _convert_html_to_md(self, html: str, base_url: str) -> str:
        """Convert HTML to markdown."""
        soup = BeautifulSoup(html, 'html.parser')

        # Try to find main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=re.compile('content|main|article')) or
            soup.body
        )

        if not main_content:
            main_content = soup

        # Remove script and style elements
        for script in main_content.find_all(['script', 'style', 'nav', 'footer']):
            script.decompose()

        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()

        h1 = main_content.find('h1')
        if h1:
            title = h1.get_text().strip()

        # Convert to markdown
        md_lines = []

        if title:
            md_lines.append(f"# {title}")
            md_lines.append("")
            md_lines.append(f"*Source: {base_url}*")
            md_lines.append("")

        # Process content
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'ul', 'ol', 'li', 'code']):
            text = element.get_text().strip()

            if not text:
                continue

            if element.name == 'h1':
                if title and text == title:
                    continue  # Skip duplicate title
                md_lines.append(f"# {text}")
            elif element.name == 'h2':
                md_lines.append(f"## {text}")
            elif element.name == 'h3':
                md_lines.append(f"### {text}")
            elif element.name == 'h4':
                md_lines.append(f"#### {text}")
            elif element.name == 'pre':
                # Code block
                code = element.get_text()
                lang = ""
                if 'class' in element.attrs:
                    classes = element['class']
                    for cls in classes:
                        if cls.startswith('language-'):
                            lang = cls.replace('language-', '')
                            break
                md_lines.append(f"```{lang}")
                md_lines.append(code)
                md_lines.append("```")
            elif element.name == 'code':
                # Inline code - skip if inside pre
                if element.parent.name != 'pre':
                    md_lines.append(f"`{text}`")
            elif element.name == 'li':
                md_lines.append(f"- {text}")
            elif element.name == 'p':
                md_lines.append(text)

            md_lines.append("")

        return "\n".join(md_lines)

    def _convert_json_to_md(self, json_text: str, url: str) -> str:
        """Convert JSON (like Swagger) to markdown."""
        import json

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            return f"```json\n{json_text}\n```"

        md_lines = []

        # Try to identify Swagger/OpenAPI
        if 'swagger' in data or 'openapi' in data:
            md_lines.append("# API Documentation")
            md_lines.append("")
            md_lines.append(f"*Source: {url}*")
            md_lines.append("")

            info = data.get('info', {})
            md_lines.append(f"## {info.get('title', 'API')}")
            md_lines.append("")
            md_lines.append(info.get('description', ''))
            md_lines.append("")

            # Document paths
            paths = data.get('paths', {})
            if paths:
                md_lines.append("## Endpoints")
                md_lines.append("")

                for path, methods in paths.items():
                    for method, details in methods.items():
                        if method in ['get', 'post', 'put', 'delete', 'patch']:
                            summary = details.get('summary', '')
                            md_lines.append(f"### {method.upper()} {path}")
                            md_lines.append("")
                            if summary:
                                md_lines.append(summary)
                                md_lines.append("")

                            # Parameters
                            params = details.get('parameters', [])
                            if params:
                                md_lines.append("**Parameters:**")
                                for param in params:
                                    name = param.get('name', '')
                                    ptype = param.get('type', param.get('schema', {}).get('type', 'unknown'))
                                    desc = param.get('description', '')
                                    required = 'required' if param.get('required') else 'optional'
                                    md_lines.append(f"- `{name}` ({ptype}, {required}): {desc}")
                                md_lines.append("")

                            # Responses
                            responses = details.get('responses', {})
                            if responses:
                                md_lines.append("**Responses:**")
                                for code, resp in responses.items():
                                    desc = resp.get('description', '')
                                    md_lines.append(f"- `{code}`: {desc}")
                                md_lines.append("")

        else:
            # Generic JSON
            md_lines.append("```json")
            md_lines.append(json.dumps(data, indent=2))
            md_lines.append("```")

        return "\n".join(md_lines)

    def get_filename_from_url(self, url: str, title: Optional[str] = None) -> str:
        """Generate a filename from URL."""
        parsed = urlparse(url)

        if title:
            # Clean title for filename
            clean_title = re.sub(r'[^\w\s-]', '', title).strip()
            clean_title = re.sub(r'[-\s]+', '-', clean_title)
            return f"{clean_title}.md"

        # Use path
        path = parsed.path.strip('/')
        if path:
            parts = path.split('/')
            return f"{parts[-1] or 'index'}.md"

        return f"{parsed.netloc}.md"
