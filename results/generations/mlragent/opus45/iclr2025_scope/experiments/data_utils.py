"""
Data utilities for loading and processing datasets.
"""
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Optional, Dict, List, Tuple
import random


class SyntheticLongContextDataset(Dataset):
    """
    Synthetic dataset for testing KV cache compression.
    Simulates long-context QA tasks with controllable "needle" positions.
    """
    def __init__(
        self,
        tokenizer,
        num_samples: int = 100,
        context_length: int = 2048,
        num_needles: int = 3,
        seed: int = 42,
    ):
        self.tokenizer = tokenizer
        self.num_samples = num_samples
        self.context_length = context_length
        self.num_needles = num_needles

        random.seed(seed)
        torch.manual_seed(seed)

        # Generate synthetic data
        self.samples = self._generate_samples()

    def _generate_samples(self) -> List[Dict]:
        samples = []
        vocab_words = [
            "the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
            "system", "model", "data", "learning", "neural", "network", "deep",
            "layer", "attention", "transformer", "cache", "memory", "token",
            "sequence", "context", "query", "key", "value", "output", "input",
        ]

        facts = [
            ("capital of France", "Paris"),
            ("largest planet", "Jupiter"),
            ("speed of light", "299792458 meters per second"),
            ("water formula", "H2O"),
            ("deepest ocean", "Pacific Ocean"),
            ("tallest mountain", "Mount Everest"),
            ("smallest country", "Vatican City"),
            ("longest river", "Amazon River"),
        ]

        for i in range(self.num_samples):
            # Select random facts as needles
            selected_facts = random.sample(facts, min(self.num_needles, len(facts)))

            # Generate filler text
            target_filler_tokens = self.context_length - 100 * self.num_needles

            filler_words = []
            for _ in range(target_filler_tokens // 2):
                filler_words.append(random.choice(vocab_words))

            filler_text = " ".join(filler_words)

            # Insert facts at random positions
            words = filler_text.split()
            needle_positions = sorted(random.sample(range(len(words)), min(self.num_needles, len(words))))

            for j, (question, answer) in enumerate(selected_facts):
                if j < len(needle_positions):
                    pos = needle_positions[j]
                    fact_text = f"[FACT: The {question} is {answer}.]"
                    words.insert(pos + j, fact_text)

            context = " ".join(words)

            # Create question about one of the facts
            target_fact = random.choice(selected_facts)
            question = f"What is the {target_fact[0]}?"
            answer = target_fact[1]

            samples.append({
                'context': context,
                'question': question,
                'answer': answer,
                'needle_positions': needle_positions,
            })

        return samples

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> Dict:
        sample = self.samples[idx]

        # Create input text
        input_text = f"Context: {sample['context']}\n\nQuestion: {sample['question']}\n\nAnswer:"

        # Tokenize
        encoding = self.tokenizer(
            input_text,
            max_length=self.context_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt',
        )

        # Tokenize answer for labels
        answer_encoding = self.tokenizer(
            sample['answer'],
            max_length=64,
            truncation=True,
            padding='max_length',
            return_tensors='pt',
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'answer_ids': answer_encoding['input_ids'].squeeze(0),
            'answer': sample['answer'],
            'needle_positions': sample['needle_positions'],
        }


class LongBenchDataset(Dataset):
    """
    Wrapper for LongBench-style evaluation datasets.
    """
    def __init__(
        self,
        tokenizer,
        dataset_name: str = "scrolls",
        subset: str = "qasper",
        split: str = "test",
        max_samples: int = 100,
        max_seq_length: int = 2048,
    ):
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        self.samples = []

        try:
            from datasets import load_dataset
            # Try to load the dataset
            if dataset_name == "scrolls":
                dataset = load_dataset(dataset_name, subset, split=split, trust_remote_code=True)
            else:
                dataset = load_dataset(dataset_name, split=split, trust_remote_code=True)

            # Process samples
            for i, item in enumerate(dataset):
                if i >= max_samples:
                    break

                if 'input' in item and 'output' in item:
                    context = item['input']
                    answer = item['output'][0] if isinstance(item['output'], list) else item['output']
                elif 'context' in item and 'answer' in item:
                    context = item['context']
                    answer = item['answer']
                elif 'question' in item and 'context' in item:
                    context = item['context']
                    answer = item.get('answer', item.get('answers', {}).get('text', [''])[0])
                else:
                    continue

                self.samples.append({
                    'context': str(context)[:max_seq_length * 4],
                    'answer': str(answer) if answer else "",
                })

        except Exception as e:
            print(f"Warning: Could not load {dataset_name}/{subset}, using synthetic data. Error: {e}")
            # Fall back to synthetic data
            self._generate_synthetic_fallback(max_samples)

    def _generate_synthetic_fallback(self, num_samples: int):
        """Generate synthetic data if real dataset is unavailable."""
        for i in range(num_samples):
            self.samples.append({
                'context': f"This is a synthetic context document {i} with various information...",
                'answer': f"answer_{i}",
            })

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict:
        sample = self.samples[idx]

        input_text = f"Context: {sample['context']}\n\nAnswer the question based on the context.\n\nAnswer:"

        encoding = self.tokenizer(
            input_text,
            max_length=self.max_seq_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt',
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'answer': sample['answer'],
        }


def create_dataloader(
    dataset: Dataset,
    batch_size: int = 4,
    shuffle: bool = False,
    num_workers: int = 0,
) -> DataLoader:
    """Create a DataLoader for the dataset."""
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True,
    )


def get_attention_weights(
    model,
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
) -> torch.Tensor:
    """
    Extract attention weights from model forward pass.
    Returns: (batch, num_layers, num_heads, seq_len, seq_len)
    """
    model.eval()
    with torch.no_grad():
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_attentions=True,
        )

    # Stack attention weights from all layers
    attention_weights = torch.stack(outputs.attentions, dim=1)
    return attention_weights
