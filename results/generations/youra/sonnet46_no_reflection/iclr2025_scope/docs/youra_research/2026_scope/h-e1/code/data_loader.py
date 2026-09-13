import torch
from datasets import load_dataset, Dataset
from transformers import PreTrainedTokenizer
from config import ExperimentConfig


class MNLIDataLoader:
    def __init__(self, config: ExperimentConfig):
        self.config = config

    def load(self, n: int = None) -> Dataset:
        count = n if n is not None else self.config.primary_n
        dataset = load_dataset(self.config.dataset_id, self.config.dataset_config)
        val_data = dataset["validation_matched"]
        selected = val_data.select(range(min(count, len(val_data))))
        return selected

    def tokenize(self, dataset: Dataset, tokenizer: PreTrainedTokenizer) -> Dataset:
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        def tokenize_fn(example):
            return tokenizer(
                example["premise"],
                example["hypothesis"],
                max_length=self.config.max_seq_len,
                padding="max_length",
                truncation=True,
                return_tensors=None,
            )

        tokenized = dataset.map(tokenize_fn, batched=False)
        return tokenized

    def get_batch(self, dataset: Dataset, idx: int) -> dict:
        item = dataset[idx]
        input_ids = torch.tensor(item["input_ids"]).unsqueeze(0)
        attention_mask = torch.tensor(item["attention_mask"]).unsqueeze(0)
        label = item["label"]
        return {"input_ids": input_ids, "attention_mask": attention_mask, "label": label}
