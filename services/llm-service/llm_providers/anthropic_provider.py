"""
Anthropic Claude LLM Provider
"""

import os
from typing import Optional

import anthropic


class AnthropicProvider:
    """
    Provider for Anthropic Claude API
    """

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate response from Claude

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Generated response
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)

        return response.content[0].text
