"""
Joint DPO + Attribute Dataset Module
Loads HH-RLHF preference pairs + OpenAssistant attribute annotations
"""

import torch
from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset
from transformers import AutoTokenizer
import random


class JointDataset(Dataset):
    """Dataset combining HH-RLHF preferences with OpenAssistant attributes"""

    def __init__(self, hh_data, oasst_data, tokenizer, max_length=512):
        self.hh_data = hh_data
        self.oasst_data = oasst_data
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Map OASST attributes to HH-RLHF samples (simplified: random matching)
        self.attribute_map = self._create_attribute_map()

    def _create_attribute_map(self):
        """Map HH-RLHF indices to OASST attribute annotations"""
        attr_map = {}
        oasst_idx = 0

        for i in range(len(self.hh_data)):
            # Cycle through OASST data
            oasst_sample = self.oasst_data[oasst_idx % len(self.oasst_data)]

            # Extract real attributes from OpenAssistant labels
            # OpenAssistant has labels with 'name' and 'value' lists
            labels = oasst_sample.get("labels", None)

            if labels and "name" in labels and "value" in labels:
                # Convert lists to dict for easier access
                label_dict = dict(zip(labels["name"], labels["value"]))

                # Extract quality, helpfulness, creativity scores (normalized to 1-5 scale)
                quality = label_dict.get("quality", 0.5)
                spam = label_dict.get("spam", 0.2)
                creativity = label_dict.get("creativity", 0.5)
            else:
                # Default to mid-range values if labels not available
                quality = 0.5
                spam = 0.2
                creativity = 0.5

            attr_map[i] = {
                "helpfulness": self._normalize_score(quality, 1, 5),
                "verbosity": self._normalize_score(spam, 1, 5, invert=True),
                "creativity": self._normalize_score(creativity, 1, 5)
            }
            oasst_idx += 1

        return attr_map

    def _normalize_score(self, value, min_val, max_val, invert=False):
        """Normalize a 0-1 score to min_val-max_val range"""
        if invert:
            value = 1.0 - value
        # Convert to integer in range [min_val, max_val]
        normalized = int(min_val + value * (max_val - min_val))
        return max(min_val, min(max_val, normalized))

    def __len__(self):
        return len(self.hh_data)

    def __getitem__(self, idx):
        sample = self.hh_data[idx]

        # Extract prompt and responses
        prompt = sample["chosen"].split("\n\nAssistant:")[0]
        chosen = sample["chosen"].split("\n\nAssistant:")[-1]
        rejected = sample["rejected"].split("\n\nAssistant:")[-1]

        # Tokenize
        prompt_ids = self.tokenizer(prompt,
                                     max_length=self.max_length,
                                     padding="max_length",
                                     truncation=True,
                                     return_tensors="pt")

        chosen_ids = self.tokenizer(chosen,
                                     max_length=self.max_length,
                                     padding="max_length",
                                     truncation=True,
                                     return_tensors="pt")

        rejected_ids = self.tokenizer(rejected,
                                       max_length=self.max_length,
                                       padding="max_length",
                                       truncation=True,
                                       return_tensors="pt")

        # Get attributes
        attrs = self.attribute_map[idx]

        return {
            "prompt_ids": prompt_ids.input_ids.squeeze(0),
            "chosen_ids": chosen_ids.input_ids.squeeze(0),
            "rejected_ids": rejected_ids.input_ids.squeeze(0),
            "attributes": torch.tensor([attrs["helpfulness"],
                                        attrs["verbosity"],
                                        attrs["creativity"]], dtype=torch.long)
        }


def load_datasets(cache_dir="../../.data_cache"):
    """Load HH-RLHF and OpenAssistant datasets"""
    hh_dataset = load_dataset("Anthropic/hh-rlhf",
                              cache_dir=f"{cache_dir}/datasets/hh-rlhf")
    oasst_dataset = load_dataset("OpenAssistant/oasst1",
                                 cache_dir=f"{cache_dir}/datasets/openassistant")

    return hh_dataset, oasst_dataset


def create_dataloaders(batch_size=4, max_length=512, cache_dir="../../.data_cache"):
    """Create train and test dataloaders"""
    # Load datasets
    hh_dataset, oasst_dataset = load_datasets(cache_dir)

    # Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained("gpt2-xl")
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    # Create datasets
    train_dataset = JointDataset(hh_dataset["train"],
                                   oasst_dataset["train"],
                                   tokenizer,
                                   max_length)

    test_dataset = JointDataset(hh_dataset["test"],
                                 oasst_dataset["validation"],
                                 tokenizer,
                                 max_length)

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader, tokenizer


if __name__ == "__main__":
    # Test dataset loading
    train_loader, test_loader, tokenizer = create_dataloaders(batch_size=2)

    print(f"Train batches: {len(train_loader)}")
    print(f"Test batches: {len(test_loader)}")

    # Test single batch
    batch = next(iter(train_loader))
    print(f"\nBatch keys: {batch.keys()}")
    print(f"Prompt shape: {batch['prompt_ids'].shape}")
    print(f"Chosen shape: {batch['chosen_ids'].shape}")
    print(f"Rejected shape: {batch['rejected_ids'].shape}")
    print(f"Attributes shape: {batch['attributes'].shape}")
    print("✓ Dataset module working")
