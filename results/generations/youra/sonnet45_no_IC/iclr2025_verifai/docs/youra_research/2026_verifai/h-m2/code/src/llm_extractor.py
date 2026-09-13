"""LLM-based semantic extraction with multi-vote consensus."""
import json
import os
import time
from typing import List, Dict, Optional
from anthropic import Anthropic

class LLMExtractor:
    """LLM-based extraction with consensus voting."""
    
    def __init__(
        self,
        model_name: str = "claude-sonnet-4-5",
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        max_retries: int = 3
    ):
        """Initialize extractor."""
        self.model = model_name
        self.temperature = temperature
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.max_retries = max_retries
    
    def extract_assumptions(self, query_text: str, prompt_template: str) -> List[str]:
        """Extract assumptions from query parameters."""
        prompt = prompt_template.replace("{QUERY_TEXT}", query_text)
        response = self._call_llm(prompt)
        return self._parse_llm_response(response)
    
    def extract_claims(self, result_text: str, prompt_template: str) -> List[str]:
        """Extract claims from result content."""
        prompt = prompt_template.replace("{RESULT_TEXT}", result_text)
        response = self._call_llm(prompt)
        return self._parse_llm_response(response)
    
    def multi_vote_extract(
        self,
        text: str,
        prompt_template: str,
        extraction_type: str,
        n_votes: int = 3,
        consensus_threshold: int = 2
    ) -> List[str]:
        """Multi-vote extraction with consensus."""
        all_votes = []
        
        for _ in range(n_votes):
            if extraction_type == "assumptions":
                items = self.extract_assumptions(text, prompt_template)
            else:
                items = self.extract_claims(text, prompt_template)
            all_votes.append(items)
        
        # Consensus: items appearing in ≥threshold votes
        item_counts = {}
        for vote in all_votes:
            for item in vote:
                item_counts[item] = item_counts.get(item, 0) + 1
        
        consensus_items = [item for item, count in item_counts.items() if count >= consensus_threshold]
        return consensus_items
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with retry logic."""
        for attempt in range(self.max_retries):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e
    
    def _parse_llm_response(self, response: str) -> List[str]:
        """Parse LLM response to extract list of items."""
        # Try JSON parsing first
        try:
            data = json.loads(response)
            if isinstance(data, list):
                return [str(item) for item in data]
            elif isinstance(data, dict) and "items" in data:
                return [str(item) for item in data["items"]]
        except json.JSONDecodeError:
            pass
        
        # Fallback: regex for numbered lists
        import re
        pattern = r'^\d+[\.\)]\s*(.+)$'
        lines = response.strip().split('\n')
        items = []
        for line in lines:
            match = re.match(pattern, line.strip())
            if match:
                items.append(match.group(1).strip())
            elif line.strip() and not line.startswith('#'):
                items.append(line.strip())
        
        return items[:20]  # Limit to 20 items
