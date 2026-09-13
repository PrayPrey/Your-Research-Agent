from datasets import load_dataset
from torch.utils.data import DataLoader, Dataset
import torch

class TextDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item

def load_sst2_splits():
    dataset = load_dataset("glue", "sst2")
    train_texts = dataset["train"]["sentence"]
    train_labels = dataset["train"]["label"]
    val_texts = dataset["validation"]["sentence"]
    val_labels = dataset["validation"]["label"]
    return train_texts, train_labels, val_texts, val_labels

def build_dataloader(tokenizer, texts, labels, batch_size, max_length=128, shuffle=True):
    encodings = tokenizer(
        list(texts),
        truncation=True,
        padding="max_length",
        max_length=max_length,
        return_tensors="pt"
    )
    dataset = TextDataset(encodings, torch.tensor(labels))
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

def collate_for_hessian(batch):
    input_ids = torch.stack([item["input_ids"] for item in batch])
    attention_mask = torch.stack([item["attention_mask"] for item in batch])
    labels = torch.stack([item["labels"] for item in batch])
    return input_ids, attention_mask, labels
