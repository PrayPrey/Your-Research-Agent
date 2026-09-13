"""
Multi-Domain Dataset Loader for GLUE + XTREME benchmarks
Based on: 03_architecture.md - Module 1: DataModule
Based on: 03_logic.md - A-5: Data Pipeline
"""

from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers import AutoTokenizer
from typing import Dict, Tuple, Any
import torch


class MultiDomainDataset:
    """Load and preprocess 17 tasks (9 GLUE + 8 XTREME) with HuggingFace datasets."""

    def __init__(self, tokenizer_name: str = "meta-llama/Llama-2-7b-hf",
                 max_length: int = 512,
                 batch_size: int = 16):
        """
        Initialize multi-domain dataset loader.

        Args:
            tokenizer_name: HuggingFace tokenizer identifier
            max_length: Maximum sequence length
            batch_size: Batch size for DataLoader
        """
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.max_length = max_length
        self.batch_size = batch_size

        # Task configurations
        self.glue_tasks = ["cola", "sst2", "mrpc", "qqp", "stsb", "mnli", "qnli", "rte", "wnli"]
        self.xtreme_langs = ["en", "es", "de", "zh"]

    def load_glue_tasks(self) -> Dict[str, Tuple[DataLoader, DataLoader]]:
        """
        Load all 9 GLUE tasks.

        Returns:
            Dictionary mapping task_name -> (train_loader, val_loader)
        """
        loaders = {}

        for task in self.glue_tasks:
            try:
                # Load dataset with new identifier
                dataset = load_dataset("nyu-mll/glue", task)

                # Get number of labels
                if task == "stsb":
                    num_labels = 1  # Regression task
                elif task == "mnli":
                    num_labels = 3  # 3-way classification
                else:
                    num_labels = 2  # Binary classification

                # Preprocess
                train_ds = dataset["train"].map(
                    lambda x: self._preprocess_glue(x, task),
                    batched=True,
                    remove_columns=dataset["train"].column_names
                )

                val_split = "validation_matched" if task == "mnli" else "validation"
                val_ds = dataset[val_split].map(
                    lambda x: self._preprocess_glue(x, task),
                    batched=True,
                    remove_columns=dataset[val_split].column_names
                )

                # Create DataLoaders
                train_loader = DataLoader(
                    train_ds,
                    batch_size=self.batch_size,
                    shuffle=True,
                    collate_fn=self._collate_fn
                )

                val_loader = DataLoader(
                    val_ds,
                    batch_size=self.batch_size,
                    shuffle=False,
                    collate_fn=self._collate_fn
                )

                loaders[task] = (train_loader, val_loader)
                print(f"✓ Loaded GLUE/{task}: {len(train_ds)} train, {len(val_ds)} val")

            except Exception as e:
                print(f"✗ Failed to load GLUE/{task}: {e}")
                continue

        return loaders

    def load_xtreme_tasks(self) -> Dict[str, Tuple[DataLoader, DataLoader]]:
        """
        Load XTREME tasks (XNLI + PAWS-X, 4 languages each = 8 tasks).

        Returns:
            Dictionary mapping task_name -> (train_loader, val_loader)
        """
        loaders = {}

        # XNLI (4 languages)
        for lang in self.xtreme_langs:
            task_name = f"xnli_{lang}"
            try:
                dataset = load_dataset("xnli", lang)

                # XNLI is 3-way classification
                train_ds = dataset["train"].map(
                    lambda x: self._preprocess_xnli(x),
                    batched=True,
                    remove_columns=dataset["train"].column_names
                )

                val_ds = dataset["validation"].map(
                    lambda x: self._preprocess_xnli(x),
                    batched=True,
                    remove_columns=dataset["validation"].column_names
                )

                train_loader = DataLoader(
                    train_ds,
                    batch_size=self.batch_size,
                    shuffle=True,
                    collate_fn=self._collate_fn
                )

                val_loader = DataLoader(
                    val_ds,
                    batch_size=self.batch_size,
                    shuffle=False,
                    collate_fn=self._collate_fn
                )

                loaders[task_name] = (train_loader, val_loader)
                print(f"✓ Loaded XNLI/{lang}: {len(train_ds)} train, {len(val_ds)} val")

            except Exception as e:
                print(f"✗ Failed to load XNLI/{lang}: {e}")
                continue

        # PAWS-X (4 languages)
        for lang in self.xtreme_langs:
            task_name = f"pawsx_{lang}"
            try:
                dataset = load_dataset("paws-x", lang)

                # PAWS-X is binary classification
                train_ds = dataset["train"].map(
                    lambda x: self._preprocess_pawsx(x),
                    batched=True,
                    remove_columns=dataset["train"].column_names
                )

                val_ds = dataset["validation"].map(
                    lambda x: self._preprocess_pawsx(x),
                    batched=True,
                    remove_columns=dataset["validation"].column_names
                )

                train_loader = DataLoader(
                    train_ds,
                    batch_size=self.batch_size,
                    shuffle=True,
                    collate_fn=self._collate_fn
                )

                val_loader = DataLoader(
                    val_ds,
                    batch_size=self.batch_size,
                    shuffle=False,
                    collate_fn=self._collate_fn
                )

                loaders[task_name] = (train_loader, val_loader)
                print(f"✓ Loaded PAWS-X/{lang}: {len(train_ds)} train, {len(val_ds)} val")

            except Exception as e:
                print(f"✗ Failed to load PAWS-X/{lang}: {e}")
                continue

        return loaders

    def get_all_tasks(self) -> Dict[str, Tuple[DataLoader, DataLoader]]:
        """
        Get all 17 tasks (GLUE + XTREME).

        Returns:
            Combined dictionary of all task loaders
        """
        all_loaders = {}

        print("Loading GLUE tasks...")
        glue_loaders = self.load_glue_tasks()
        all_loaders.update(glue_loaders)

        print("\nLoading XTREME tasks...")
        xtreme_loaders = self.load_xtreme_tasks()
        all_loaders.update(xtreme_loaders)

        print(f"\n✓ Total tasks loaded: {len(all_loaders)}/17")
        return all_loaders

    def _preprocess_glue(self, examples: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Preprocess GLUE task examples."""
        # Different GLUE tasks have different input formats
        if task in ["mrpc", "qqp", "stsb", "mnli", "qnli", "rte"]:
            # Sentence pair tasks
            sentence1 = examples["sentence1"] if "sentence1" in examples else examples.get("premise", examples.get("question", []))
            sentence2 = examples["sentence2"] if "sentence2" in examples else examples.get("hypothesis", examples.get("sentence", []))

            encodings = self.tokenizer(
                sentence1,
                sentence2,
                truncation=True,
                padding="max_length",
                max_length=self.max_length,
                return_tensors=None  # Return lists, not tensors
            )
        else:
            # Single sentence tasks (cola, sst2, wnli)
            sentences = examples["sentence"]
            encodings = self.tokenizer(
                sentences,
                truncation=True,
                padding="max_length",
                max_length=self.max_length,
                return_tensors=None
            )

        encodings["labels"] = examples["label"]
        return encodings

    def _preprocess_xnli(self, examples: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess XNLI examples."""
        encodings = self.tokenizer(
            examples["premise"],
            examples["hypothesis"],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors=None
        )
        encodings["labels"] = examples["label"]
        return encodings

    def _preprocess_pawsx(self, examples: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess PAWS-X examples."""
        encodings = self.tokenizer(
            examples["sentence1"],
            examples["sentence2"],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors=None
        )
        encodings["labels"] = examples["label"]
        return encodings

    def _collate_fn(self, batch):
        """Custom collate function to convert lists to tensors."""
        # Convert to tensors
        input_ids = torch.tensor([item["input_ids"] for item in batch])
        attention_mask = torch.tensor([item["attention_mask"] for item in batch])
        labels = torch.tensor([item["labels"] for item in batch])

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }
