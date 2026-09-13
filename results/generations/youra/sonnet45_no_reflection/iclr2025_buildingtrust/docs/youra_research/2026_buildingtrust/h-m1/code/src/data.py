"""Dataset loading and preprocessing for H-E1"""
from datasets import load_dataset, Dataset
from transformers import PreTrainedTokenizer
from typing import Dict, List, Optional
import torch

class TrustworthinessDataset:
    """Dataset loader for trustworthiness benchmarks"""

    def __init__(self, dimension: str, split: str = "validation"):
        """Initialize dataset loader for specific dimension.

        Args:
            dimension: One of "truthfulness", "fairness", "robustness"
            split: Dataset split to load
        """
        self.dimension = dimension
        self.split = split
        self.data: Optional[Dataset] = None

        # Load appropriate dataset based on dimension
        if dimension == "truthfulness":
            self.data = self.load_truthfulqa()
        elif dimension == "fairness":
            self.data = self.load_bbq()
        elif dimension == "robustness":
            self.data = self.load_advglue()
        else:
            raise ValueError(f"Unknown dimension: {dimension}")

    def load_truthfulqa(self) -> Dataset:
        """Load TruthfulQA dataset. Returns HF Dataset with 817 samples."""
        dataset = load_dataset("truthful_qa", "multiple_choice")
        return dataset["validation"]

    def load_bbq(self) -> Dataset:
        """Load BBQ dataset. Returns HF Dataset."""
        # Load one category for PoC (Age category)
        dataset = load_dataset("HiTZ/bbq", "Age_disambig")
        return dataset["test"]

    def load_advglue(self) -> Dataset:
        """Load AdvGLUE dataset. Returns HF Dataset."""
        dataset = load_dataset("adv_glue", "adv_sst2")
        return dataset["validation"]

    def __len__(self) -> int:
        """Dataset length."""
        return len(self.data) if self.data is not None else 0

    def __getitem__(self, idx: int) -> Dict:
        """Get item. Returns dataset entry."""
        if self.data is None:
            raise ValueError("Dataset not loaded")
        return self.data[idx]


class DataCollator:
    """Collate batch with tokenization"""

    def __init__(self, tokenizer: PreTrainedTokenizer, max_length: int = 512):
        """Initialize collator with tokenizer.

        Args:
            tokenizer: HuggingFace tokenizer
            max_length: Maximum sequence length
        """
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(self, features: List[Dict]) -> Dict[str, torch.Tensor]:
        """Collate batch.

        Args:
            features: List of dataset entries

        Returns:
            Dictionary with input_ids, attention_mask, labels
        """
        # Extract text based on dataset structure
        texts = []
        labels = []

        for feature in features:
            # Handle different dataset formats
            if "question" in feature:
                # TruthfulQA format
                text = feature["question"]
                label = feature.get("mc1_targets", {}).get("labels", [0])[0]
            elif "context" in feature:
                # BBQ format
                text = f"{feature['context']} {feature['question']}"
                label = feature.get("label", 0)
            elif "sentence" in feature:
                # AdvGLUE format
                text = feature["sentence"]
                label = feature.get("label", 0)
            else:
                # Fallback
                text = str(feature)
                label = 0

            texts.append(text)
            labels.append(label)

        # Tokenize
        encodings = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )

        # For causal LM, labels should be input_ids (next token prediction)
        encodings["labels"] = encodings["input_ids"].clone()

        return encodings
