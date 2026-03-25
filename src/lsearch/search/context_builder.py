"""Build context from search results with token limit management."""

from typing import List, Dict, Any
import tiktoken

from lsearch.config import Config


class ContextBuilder:
    """Builds context from search results respecting token limits."""

    def __init__(self, config: Config):
        self.config = config
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except Exception:
            # Fallback to cl100k_base
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))

    def build_context(
        self,
        results: List[Dict[str, Any]],
        max_tokens: int = None,
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Build context from search results.

        Returns:
            {
                "content": str,  # The combined context
                "used_results": List[Dict],  # Results that fit
                "excluded_results": List[Dict],  # Results that didn't fit
                "total_tokens": int,
                "truncated": bool,
            }
        """
        if max_tokens is None:
            max_tokens = self.config.token_limit

        context_parts = []
        used_results = []
        excluded_results = []
        current_tokens = 0

        # Reserve tokens for header
        header = "## Knowledge Base Context\n\n"
        header_tokens = self.count_tokens(header)
        current_tokens += header_tokens

        for result in results:
            # Build the text for this result
            text = self._format_result(result, include_metadata)
            tokens = self.count_tokens(text)

            if current_tokens + tokens > max_tokens:
                excluded_results.append(result)
            else:
                context_parts.append(text)
                used_results.append(result)
                current_tokens += tokens

        content = header + "\n---\n\n".join(context_parts)

        # Add summary if truncated
        if excluded_results:
            summary = f"\n\n*[找到 {len(results)} 篇相关文档，已选取最相关的 {len(used_results)} 篇]*"
            content += summary
            current_tokens += self.count_tokens(summary)

        return {
            "content": content,
            "used_results": used_results,
            "excluded_results": excluded_results,
            "total_tokens": current_tokens,
            "truncated": len(excluded_results) > 0,
            "total_results": len(results),
        }

    def _format_result(self, result: Dict[str, Any], include_metadata: bool) -> str:
        """Format a single result as context text."""
        meta = result["metadata"]
        text = result["text"]

        parts = []

        # Add header with source info
        if include_metadata:
            file_path = meta.get("file_path", "unknown")
            title = meta.get("title", "")

            if title:
                parts.append(f"### {title}")
            else:
                parts.append(f"### Source: {file_path}")

            parts.append(f"*File: {file_path}*\n")

        # Add content
        parts.append(text)

        return "\n".join(parts)

    def interactive_select(
        self,
        results: List[Dict[str, Any]],
        max_tokens: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Return results that can fit, prompting for user selection if needed.

        This is a placeholder for interactive selection logic.
        In practice, this would be handled by the skill/Claude.
        """
        if max_tokens is None:
            max_tokens = self.config.token_limit

        # First, try to fit as many as possible
        context = self.build_context(results, max_tokens)

        if not context["truncated"]:
            return results

        # If truncated, we need user interaction
        # This is handled at the skill level
        return context["used_results"]
