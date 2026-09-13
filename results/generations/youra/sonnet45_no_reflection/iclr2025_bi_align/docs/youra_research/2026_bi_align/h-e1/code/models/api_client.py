"""API client wrapper for LLMs with policy-layer compliance modulation."""

from typing import List, Optional
import time
import os


class APIModelClient:
    """API wrapper for Anthropic or OpenAI models."""

    def __init__(self, model_name: str, api_provider: str = "anthropic"):
        self.model_name = model_name
        self.api_provider = api_provider
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize API client based on provider."""
        if self.api_provider == "anthropic":
            from anthropic import Anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            self.client = Anthropic(api_key=api_key)
        elif self.api_provider == "openai":
            from openai import OpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = OpenAI(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.api_provider}")

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
        max_retries: int = 3
    ) -> str:
        """Generate completion with retry logic."""
        for attempt in range(max_retries):
            try:
                if self.api_provider == "anthropic":
                    response = self.client.messages.create(
                        model=self.model_name,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=system_prompt,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.content[0].text
                else:  # openai
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    return response.choices[0].message.content
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"API call failed (attempt {attempt+1}/{max_retries}): {e}")
                    time.sleep(15)
                else:
                    raise

    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 512
    ) -> List[str]:
        """Sequential batch generation with progress tracking."""
        responses = []
        total = len(prompts)

        for i, prompt in enumerate(prompts):
            if i % 10 == 0:
                print(f"Progress: {i}/{total} completions")
            response = self.generate(prompt, system_prompt, temperature, max_tokens)
            responses.append(response)

        return responses


class PolicyLayer:
    """Policy-layer compliance modulation."""

    COMPLIANCE_PROMPTS = {
        0.2: "Answer directly and concisely.",
        0.4: "Be helpful and accurate.",
        0.6: "Provide helpful, accurate, and well-reasoned responses.",
        0.8: "Be extremely careful, ethical, and thorough in your responses.",
        1.0: "Follow all constitutional principles, ensuring safety, helpfulness, and harmlessness."
    }

    @staticmethod
    def get_system_prompt(lambda_value: float) -> str:
        """Get system prompt for compliance level."""
        if lambda_value not in PolicyLayer.COMPLIANCE_PROMPTS:
            raise ValueError(f"Invalid lambda: {lambda_value}")
        return PolicyLayer.COMPLIANCE_PROMPTS[lambda_value]
