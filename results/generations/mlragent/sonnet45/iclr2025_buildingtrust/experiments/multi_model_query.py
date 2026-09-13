"""
Multi-Model Ensemble Query System
Queries multiple LLMs and collects responses
"""
import os
import time
from typing import List, Dict
import openai
from anthropic import Anthropic


class MultiModelQuerySystem:
    """System for querying multiple LLMs and collecting responses"""

    def __init__(self, config: Dict):
        self.config = config
        self.models = config['models']
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 512)
        self.timeout = config.get('timeout', 30)

        # Initialize API clients
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    def query_gpt(self, model: str, prompt: str, temperature: float = 0.7) -> str:
        """Query OpenAI GPT models"""
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error querying {model}: {e}")
            return f"[Error: {str(e)}]"

    def query_claude(self, model: str, prompt: str, temperature: float = 0.7) -> str:
        """Query Anthropic Claude models"""
        try:
            message = self.anthropic_client.messages.create(
                model=model,
                max_tokens=self.max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            print(f"Error querying {model}: {e}")
            return f"[Error: {str(e)}]"

    def query_model(self, model: str, prompt: str, temperature: float = 0.7) -> str:
        """Route query to appropriate API based on model name"""
        if 'gpt' in model.lower():
            return self.query_gpt(model, prompt, temperature)
        elif 'claude' in model.lower():
            return self.query_claude(model, prompt, temperature)
        else:
            raise ValueError(f"Unknown model type: {model}")

    def query_ensemble(self, question: str, n_samples: int = 2) -> List[Dict]:
        """
        Query all models in the ensemble multiple times
        Returns list of responses with metadata
        """
        all_responses = []

        for model_name in self.models:
            print(f"  Querying {model_name}...", end=' ')

            for sample_idx in range(n_samples):
                try:
                    response = self.query_model(
                        model_name,
                        question,
                        temperature=self.temperature
                    )

                    all_responses.append({
                        'model': model_name,
                        'sample_idx': sample_idx,
                        'response': response,
                        'timestamp': time.time(),
                    })

                    # Add a small delay to avoid rate limits
                    time.sleep(0.5)

                except Exception as e:
                    print(f"Error: {e}")
                    all_responses.append({
                        'model': model_name,
                        'sample_idx': sample_idx,
                        'response': f"[Error: {str(e)}]",
                        'timestamp': time.time(),
                        'error': True,
                    })

            print(f"Done ({n_samples} samples)")

        return all_responses

    def batch_query_ensemble(self, questions: List[str], n_samples: int = 2) -> Dict[str, List[Dict]]:
        """
        Query ensemble for multiple questions
        Returns dict mapping question to responses
        """
        results = {}

        for idx, question in enumerate(questions):
            print(f"\nProcessing question {idx + 1}/{len(questions)}")
            responses = self.query_ensemble(question, n_samples)
            results[question] = responses

            # Add delay between questions to avoid rate limits
            if idx < len(questions) - 1:
                time.sleep(1)

        return results
