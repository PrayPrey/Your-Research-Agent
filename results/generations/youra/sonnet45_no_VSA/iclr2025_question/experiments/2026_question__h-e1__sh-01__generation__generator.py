"""Response generator using OpenAI API."""

import openai
import json
import time
import os
from typing import List, Dict, Tuple
from tqdm import tqdm


class ResponseGenerator:
    """Generate responses using GPT-3.5-turbo with token alternatives."""

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7, api_key: str = None):
        self.model = model
        self.temperature = temperature

        # Set API key
        if api_key:
            openai.api_key = api_key
        elif "OPENAI_API_KEY" in os.environ:
            openai.api_key = os.environ["OPENAI_API_KEY"]
        else:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")

    def generate_responses(
        self,
        prompts: List[Dict],
        max_tokens: int = 200,
        checkpoint_path: str = None,
        checkpoint_interval: int = 50
    ) -> List[Dict]:
        """Generate responses for all prompts with checkpointing.

        Args:
            prompts: List of dicts with 'question' and 'domain' keys
            max_tokens: Maximum tokens per response
            checkpoint_path: Path to save checkpoints
            checkpoint_interval: Save checkpoint every N responses

        Returns:
            List of dicts with 'question', 'response', and 'domain' keys
        """
        # Try to load from checkpoint
        responses = []
        start_idx = 0
        if checkpoint_path and os.path.exists(checkpoint_path):
            print(f"Loading checkpoint from {checkpoint_path}")
            responses = self.load_checkpoint(checkpoint_path)
            start_idx = len(responses)
            print(f"Resuming from index {start_idx}")

        # Generate remaining responses
        for idx in tqdm(range(start_idx, len(prompts)), desc="Generating responses"):
            prompt = prompts[idx]
            success = False
            retries = 0
            max_retries = 3

            while not success and retries < max_retries:
                try:
                    # Call OpenAI API
                    response = openai.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "user", "content": prompt["question"]}
                        ],
                        temperature=self.temperature,
                        max_tokens=max_tokens,
                        logprobs=True,
                        top_logprobs=10  # Get K=10 alternatives
                    )

                    # Extract response and token alternatives
                    response_text = response.choices[0].message.content
                    logprobs = response.choices[0].logprobs

                    # Store result
                    result = {
                        "question": prompt["question"],
                        "response": response_text,
                        "domain": prompt["domain"],
                        "logprobs": logprobs.model_dump() if logprobs else None,
                        "idx": prompt.get("idx", idx)
                    }
                    responses.append(result)
                    success = True

                    # Rate limiting
                    time.sleep(1.0)  # ~60 requests/min

                except openai.RateLimitError as e:
                    retries += 1
                    wait_time = 2 ** retries  # Exponential backoff
                    print(f"Rate limit hit, waiting {wait_time}s (retry {retries}/{max_retries})")
                    time.sleep(wait_time)

                except Exception as e:
                    retries += 1
                    print(f"Error generating response for idx {idx}: {e}")
                    if retries >= max_retries:
                        print(f"Failed after {max_retries} retries, skipping...")
                        # Add placeholder
                        responses.append({
                            "question": prompt["question"],
                            "response": "",
                            "domain": prompt["domain"],
                            "logprobs": None,
                            "error": str(e),
                            "idx": prompt.get("idx", idx)
                        })
                        success = True
                    else:
                        wait_time = 2 ** retries
                        time.sleep(wait_time)

            # Save checkpoint
            if checkpoint_path and (idx + 1) % checkpoint_interval == 0:
                self.save_checkpoint(responses, checkpoint_path)
                print(f"Checkpoint saved at index {idx + 1}")

        # Final checkpoint save
        if checkpoint_path:
            self.save_checkpoint(responses, checkpoint_path)

        return responses

    def get_token_alternatives(self, logprobs_data: Dict, K: int = 10) -> Tuple[List[str], List[List[Tuple[str, float]]]]:
        """Extract token alternatives from logprobs.

        Args:
            logprobs_data: Logprobs data from OpenAI response
            K: Number of alternatives per token

        Returns:
            Tuple of (tokens, alternatives) where alternatives is list of (token, prob) tuples
        """
        if not logprobs_data or "content" not in logprobs_data:
            return [], []

        tokens = []
        alternatives = []

        for token_data in logprobs_data["content"]:
            # Main token
            tokens.append(token_data["token"])

            # Top-K alternatives
            token_alternatives = []
            if "top_logprobs" in token_data and token_data["top_logprobs"]:
                for alt in token_data["top_logprobs"][:K]:
                    token_str = alt["token"]
                    logprob = alt["logprob"]
                    prob = 2.0 ** logprob  # Convert logprob to probability
                    token_alternatives.append((token_str, prob))

            alternatives.append(token_alternatives)

        return tokens, alternatives

    def save_checkpoint(self, responses: List[Dict], path: str):
        """Save responses to checkpoint file."""
        with open(path, 'w') as f:
            json.dump(responses, f, indent=2)

    def load_checkpoint(self, path: str) -> List[Dict]:
        """Load responses from checkpoint file."""
        with open(path, 'r') as f:
            return json.load(f)
