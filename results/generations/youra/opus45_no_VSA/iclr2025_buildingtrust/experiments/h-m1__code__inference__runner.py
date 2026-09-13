"""Run paraphrase inference on models for BSI computation."""

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datasets import Dataset
from tqdm import tqdm


class InferenceRunner:
    """Run paraphrase classification inference."""

    def __init__(self, model_id: str, batch_size: int = 32, max_length: int = 256, device: str = None):
        self.model_id = model_id
        self.batch_size = batch_size
        self.max_length = max_length
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_id, trust_remote_code=True
        ).to(self.device)
        self.model.eval()

    def predict(self, dataset: Dataset, text1_col: str, text2_col: str) -> np.ndarray:
        """
        Predict paraphrase labels (0/1) for dataset pairs.

        Args:
            dataset: HF Dataset with text pair columns
            text1_col: First text column name
            text2_col: Second text column name

        Returns:
            preds: (N,) array of 0/1 predictions
        """
        preds = []

        for i in tqdm(range(0, len(dataset), self.batch_size), desc=f"Inference {self.model_id}"):
            batch = dataset[i:i + self.batch_size]
            texts1 = batch[text1_col]
            texts2 = batch[text2_col]

            inputs = self.tokenizer(
                texts1, texts2,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                batch_preds = torch.argmax(logits, dim=-1).cpu().numpy()

            preds.extend(batch_preds.tolist())

        return np.array(preds)

    def accuracy(self, preds: np.ndarray, labels: np.ndarray) -> float:
        """Compute accuracy."""
        return float(np.mean(preds == labels))


def compute_model_accuracy_on_dataset(
    model_id: str,
    dataset: Dataset,
    text1_col: str,
    text2_col: str,
    label_col: str = "label",
    batch_size: int = 32,
    max_length: int = 256
) -> float:
    """Convenience function: load model, run inference, return accuracy."""
    runner = InferenceRunner(model_id, batch_size, max_length)
    preds = runner.predict(dataset, text1_col, text2_col)
    labels = np.array(dataset[label_col])
    return runner.accuracy(preds, labels)
