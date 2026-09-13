"""Dataset loader for TruthfulQA and WritingPrompts."""

from datasets import load_dataset
import numpy as np
from typing import List, Dict
import random


class DataLoader:
    """Load and prepare datasets for CCP evaluation."""

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        np.random.seed(random_seed)
        random.seed(random_seed)

    def load_truthfulqa(self, sample_size: int = 200) -> List[Dict]:
        """Load TruthfulQA dataset with stratified sampling.

        Args:
            sample_size: Number of samples to extract

        Returns:
            List of dicts with 'question' and 'domain' keys
        """
        print(f"Loading TruthfulQA dataset (sample_size={sample_size})...")
        dataset = load_dataset("truthfulqa/truthful_qa", "generation", trust_remote_code=True)
        validation_data = dataset["validation"]

        # Convert to list of dicts
        all_examples = []
        for idx, example in enumerate(validation_data):
            all_examples.append({
                "question": example["question"],
                "domain": "factual",
                "category": example.get("category", "unknown"),
                "idx": idx
            })

        # Stratified sampling by category
        samples = self.stratified_sample(all_examples, key="category", n=sample_size)
        print(f"Loaded {len(samples)} TruthfulQA samples from {len(set(s['category'] for s in samples))} categories")
        return samples

    def load_writingprompts(self, sample_size: int = 200) -> List[Dict]:
        """Load WritingPrompts dataset with stratified sampling.

        Args:
            sample_size: Number of samples to extract

        Returns:
            List of dicts with 'question' and 'domain' keys
        """
        print(f"Loading WritingPrompts dataset (sample_size={sample_size})...")
        dataset = load_dataset("RLAIF/WritingPrompts-Filtered", trust_remote_code=True)
        train_data = dataset["train"]

        # Convert to list of dicts and add length quartile for stratification
        all_examples = []
        for idx, example in enumerate(train_data):
            prompt = example["post_text"]
            length = len(prompt.split())
            all_examples.append({
                "question": prompt,
                "domain": "creative",
                "length": length,
                "idx": idx
            })

        # Add length quartile for stratification
        lengths = [e["length"] for e in all_examples]
        quartiles = np.percentile(lengths, [25, 50, 75])
        for example in all_examples:
            if example["length"] <= quartiles[0]:
                example["length_quartile"] = "q1"
            elif example["length"] <= quartiles[1]:
                example["length_quartile"] = "q2"
            elif example["length"] <= quartiles[2]:
                example["length_quartile"] = "q3"
            else:
                example["length_quartile"] = "q4"

        # Stratified sampling by length quartile
        samples = self.stratified_sample(all_examples, key="length_quartile", n=sample_size)
        print(f"Loaded {len(samples)} WritingPrompts samples from 4 length quartiles")
        return samples

    def stratified_sample(self, data: List[Dict], key: str, n: int) -> List[Dict]:
        """Perform stratified sampling based on a key.

        Args:
            data: List of examples
            key: Key to use for stratification
            n: Target sample size

        Returns:
            Stratified sample of size n
        """
        # Group by stratification key
        groups = {}
        for example in data:
            group_key = example[key]
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(example)

        # Calculate samples per group (proportional allocation)
        total = len(data)
        samples_per_group = {}
        for group_key, examples in groups.items():
            proportion = len(examples) / total
            samples_per_group[group_key] = max(1, int(n * proportion))

        # Adjust to ensure exactly n samples
        total_allocated = sum(samples_per_group.values())
        if total_allocated < n:
            # Add extras to largest groups
            sorted_groups = sorted(groups.keys(), key=lambda k: len(groups[k]), reverse=True)
            for i in range(n - total_allocated):
                samples_per_group[sorted_groups[i % len(sorted_groups)]] += 1
        elif total_allocated > n:
            # Remove extras from largest groups
            sorted_groups = sorted(groups.keys(), key=lambda k: len(groups[k]), reverse=True)
            for i in range(total_allocated - n):
                if samples_per_group[sorted_groups[i % len(sorted_groups)]] > 1:
                    samples_per_group[sorted_groups[i % len(sorted_groups)]] -= 1

        # Sample from each group
        stratified_samples = []
        for group_key, count in samples_per_group.items():
            group_samples = groups[group_key]
            if len(group_samples) <= count:
                stratified_samples.extend(group_samples)
            else:
                sampled = random.sample(group_samples, count)
                stratified_samples.extend(sampled)

        # Shuffle to avoid ordering bias
        random.shuffle(stratified_samples)

        return stratified_samples[:n]
