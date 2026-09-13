"""HumanEval dataset loader and preprocessor."""

import logging
from datasets import load_dataset
from typing import List, Dict

logger = logging.getLogger(__name__)

class HumanEvalLoader:
    def __init__(self, cache_dir: str = "./data/humaneval"):
        self.cache_dir = cache_dir
        self.dataset = None
        self.problems = None

    def load_dataset(self):
        """Load HumanEval from HuggingFace Hub."""
        logger.info("Loading HumanEval dataset...")
        self.dataset = load_dataset("openai/openai_humaneval", split="test", cache_dir=self.cache_dir)
        logger.info(f"Loaded {len(self.dataset)} problems from HumanEval")
        return self.dataset

    def prepare_training_prompts(self) -> List[str]:
        """Extract function signature + docstring for training."""
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")

        prompts = [item["prompt"] for item in self.dataset]
        logger.info(f"Prepared {len(prompts)} training prompts")
        return prompts

    def prepare_test_suites(self) -> List[Dict]:
        """Extract test cases and entry points for evaluation."""
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")

        test_suites = []
        for item in self.dataset:
            test_suites.append({
                "task_id": item["task_id"],
                "prompt": item["prompt"],
                "test": item["test"],
                "entry_point": item["entry_point"],
                "canonical_solution": item.get("canonical_solution", "")
            })

        logger.info(f"Prepared {len(test_suites)} test suites")
        return test_suites

    def get_sft_pairs(self) -> List[Dict]:
        """Get (prompt, solution) pairs for SFT training."""
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")

        pairs = []
        for item in self.dataset:
            pairs.append({
                "prompt": item["prompt"],
                "solution": item["canonical_solution"]
            })

        logger.info(f"Prepared {len(pairs)} SFT training pairs")
        return pairs
