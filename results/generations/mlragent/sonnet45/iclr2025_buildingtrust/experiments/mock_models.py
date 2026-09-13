"""
Mock Model System for Testing
Simulates multiple LLM responses with controlled disagreement patterns
"""
import random
import hashlib
from typing import List, Dict


class MockModelSystem:
    """Simulate multiple models with different response patterns"""

    def __init__(self, models: List[str], seed: int = 42):
        self.models = models
        self.seed = seed
        random.seed(seed)

    def _hash_question(self, question: str, model: str, sample_idx: int) -> int:
        """Create deterministic hash from question, model, and sample index"""
        combined = f"{question}_{model}_{sample_idx}"
        return int(hashlib.md5(combined.encode()).hexdigest(), 16)

    def _generate_answer_variants(self, correct_answer: str, hash_val: int) -> str:
        """Generate answer variants based on hash"""
        rng = random.Random(hash_val)

        # Decide if this model gets it right (70% accuracy)
        if rng.random() < 0.7:
            # Correct answer with variations
            variants = [
                correct_answer,
                correct_answer.upper(),
                correct_answer.lower(),
                f"The answer is {correct_answer}",
                f"{correct_answer} is the correct answer",
            ]
            return rng.choice(variants)
        else:
            # Incorrect answer
            wrong_answers = [
                "I'm not sure about this question.",
                "Unknown",
                "I don't have enough information",
                "That's a difficult question",
            ]
            return rng.choice(wrong_answers)

    def _add_explanation(self, answer: str, hash_val: int) -> str:
        """Add explanation to make responses more varied"""
        rng = random.Random(hash_val + 1000)

        explanations = [
            f"{answer}. This is a well-known fact.",
            f"Based on my knowledge, {answer}.",
            f"The correct answer is {answer}. Let me explain why.",
            f"{answer}. This has been established through research.",
            f"After careful consideration, I believe {answer}.",
        ]

        if rng.random() < 0.5:
            return rng.choice(explanations)
        return answer

    def query_model(self, model: str, question: str, sample_idx: int,
                    correct_answer: str = None) -> str:
        """Simulate querying a single model"""
        hash_val = self._hash_question(question, model, sample_idx)

        if correct_answer is None:
            # Generic answer when we don't know the truth
            rng = random.Random(hash_val)
            generic_answers = [
                "This is a complex question that requires careful analysis.",
                "There are multiple perspectives on this topic.",
                "The answer depends on various factors.",
            ]
            return rng.choice(generic_answers)

        # Generate answer variant
        answer = self._generate_answer_variants(correct_answer, hash_val)
        answer_with_explanation = self._add_explanation(answer, hash_val)

        return answer_with_explanation

    def query_ensemble(self, question: str, n_samples: int = 2,
                       correct_answer: str = None) -> List[Dict]:
        """Query all models in ensemble"""
        all_responses = []

        for model_name in self.models:
            for sample_idx in range(n_samples):
                response_text = self.query_model(
                    model_name, question, sample_idx, correct_answer
                )

                all_responses.append({
                    'model': model_name,
                    'sample_idx': sample_idx,
                    'response': response_text,
                    'timestamp': 0,
                })

        return all_responses

    def batch_query_ensemble(self, questions: List[str],
                             correct_answers: List[str] = None,
                             n_samples: int = 2) -> Dict[str, List[Dict]]:
        """Query ensemble for multiple questions"""
        results = {}

        for idx, question in enumerate(questions):
            correct_answer = correct_answers[idx] if correct_answers else None
            responses = self.query_ensemble(question, n_samples, correct_answer)
            results[question] = responses

        return results
