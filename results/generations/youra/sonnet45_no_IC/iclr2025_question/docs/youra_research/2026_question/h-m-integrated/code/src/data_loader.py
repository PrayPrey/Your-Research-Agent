"""Multi-dataset loader for uncertainty quantification experiment."""

from typing import Optional
import torch
from datasets import load_dataset, Dataset
from torch.utils.data import DataLoader
from transformers import AutoTokenizer


class MultiDatasetLoader:
    """Load and preprocess multiple datasets for UQ experiment."""

    def __init__(
        self,
        datasets: list[str],
        tokenizer_name: str = "meta-llama/Llama-2-7b-hf",
        max_length: int = 512,
        calibration_size: int = 1000,
        test_size: int = 1000
    ):
        """Initialize multi-dataset loader."""
        self.datasets = datasets
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.max_length = max_length
        self.calibration_size = calibration_size
        self.test_size = test_size

        self.loaded_datasets = {}

    def load_all_datasets(self):
        """Load all configured datasets."""
        for dataset_name in self.datasets:
            print(f"  Loading {dataset_name}...")
            self.loaded_datasets[dataset_name] = self._load_single_dataset(dataset_name)
        return self.loaded_datasets

    def _load_single_dataset(self, name: str) -> dict:
        """Load single dataset from HuggingFace."""

        if name == "truthful_qa":
            dataset = load_dataset("truthful_qa", "generation")
            split = dataset["validation"]

            # Extract questions
            questions = []
            for item in split:
                questions.append({
                    "question": item["question"],
                    "correct_answers": item.get("correct_answers", []),
                    "incorrect_answers": item.get("incorrect_answers", [])
                })

        elif name == "Anthropic/hh-rlhf":
            dataset = load_dataset("Anthropic/hh-rlhf")
            split = dataset["test"]

            # Extract dialogues
            questions = []
            for idx, item in enumerate(split):
                if idx >= self.calibration_size + self.test_size:
                    break

                # Handle both dict and string formats
                if isinstance(item, dict):
                    chosen_text = item.get("chosen", "")
                elif isinstance(item, str):
                    chosen_text = item
                else:
                    continue

                if chosen_text and "Human:" in chosen_text:
                    # Extract human turn
                    try:
                        human_turn = chosen_text.split("Human:")[1].split("Assistant:")[0].strip()
                        questions.append({
                            "question": human_turn,
                            "correct_answers": [],
                            "incorrect_answers": []
                        })
                    except (IndexError, AttributeError):
                        continue

        elif name == "squad":
            dataset = load_dataset("squad")
            split = dataset["validation"]

            # Extract QA pairs
            questions = []
            for idx, item in enumerate(split):
                if idx >= self.calibration_size + self.test_size:
                    break

                # Handle different formats
                try:
                    if isinstance(item, dict):
                        question_text = item.get("question", "")
                        context = item.get("context", "")
                        answers = item.get("answers", {})

                        if isinstance(answers, dict) and "text" in answers:
                            correct_ans = answers["text"][0] if answers["text"] else ""
                        else:
                            correct_ans = ""

                        questions.append({
                            "question": question_text,
                            "context": context,
                            "correct_answers": [correct_ans] if correct_ans else [],
                            "incorrect_answers": []
                        })
                except (KeyError, TypeError, IndexError):
                    continue
        else:
            raise ValueError(f"Unknown dataset: {name}")

        # Split into calibration and test
        calibration = questions[:self.calibration_size]
        test = questions[self.calibration_size:self.calibration_size + self.test_size]

        return {
            "calibration": calibration,
            "test": test,
            "full": questions
        }

    def get_split(self, dataset_name: str, split: str = "test") -> list:
        """Get specific split of a dataset."""
        if dataset_name not in self.loaded_datasets:
            self.loaded_datasets[dataset_name] = self._load_single_dataset(dataset_name)
        return self.loaded_datasets[dataset_name][split]
