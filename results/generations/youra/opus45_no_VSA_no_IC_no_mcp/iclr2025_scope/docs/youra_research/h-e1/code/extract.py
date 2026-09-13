"""H-E1: SuperGLUE data loading and BERT CLS extraction."""

import numpy as np
import torch
from datasets import load_dataset
from transformers import AutoModel, AutoTokenizer
from tqdm import tqdm

from config import MODEL_NAME, SUPERGLUE_TASKS, MAX_SAMPLES_PER_TASK, MAX_SEQ_LEN


def get_text_from_sample(sample: dict, task: str) -> str:
    """Extract text from SuperGLUE sample based on task format."""
    if task == "boolq":
        return f"{sample['question']} [SEP] {sample['passage']}"
    elif task == "cb":
        return f"{sample['premise']} [SEP] {sample['hypothesis']}"
    elif task == "copa":
        return f"{sample['premise']} [SEP] {sample['choice1']} [SEP] {sample['choice2']}"
    elif task == "wic":
        return f"{sample['word']} [SEP] {sample['sentence1']} [SEP] {sample['sentence2']}"
    elif task == "wsc":
        return f"{sample['text']} [SEP] {sample['span1_text']} [SEP] {sample['span2_text']}"
    else:
        raise ValueError(f"Unknown task: {task}")


def load_superglue_samples(task: str, max_samples: int) -> list[dict]:
    """Load validation samples from a SuperGLUE task."""
    ds = load_dataset("super_glue", task, split="validation", trust_remote_code=True)
    samples = list(ds)
    if len(samples) > max_samples:
        samples = samples[:max_samples]
    return samples


def extract_cls_embeddings(
    texts: list[str],
    model,
    tokenizer,
    device: str,
    batch_size: int = 16,
) -> np.ndarray:
    """Extract last-layer [CLS] embeddings from BERT."""
    model.eval()
    all_embeddings = []

    for i in tqdm(range(0, len(texts), batch_size), desc="Extracting embeddings"):
        batch_texts = texts[i : i + batch_size]
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=MAX_SEQ_LEN,
            return_tensors="pt",
        ).to(device)

        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
            cls_emb = outputs.hidden_states[-1][:, 0, :].cpu().numpy()
            all_embeddings.append(cls_emb)

    return np.vstack(all_embeddings)


def build_dataset() -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Build full dataset: embeddings, task labels, task names."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME, output_hidden_states=True).to(device)

    all_embeddings = []
    all_labels = []

    for task_idx, task in enumerate(SUPERGLUE_TASKS):
        print(f"Loading {task}...")
        samples = load_superglue_samples(task, MAX_SAMPLES_PER_TASK)
        texts = [get_text_from_sample(s, task) for s in samples]

        embeddings = extract_cls_embeddings(texts, model, tokenizer, device)
        all_embeddings.append(embeddings)
        all_labels.extend([task_idx] * len(texts))
        print(f"  {task}: {len(texts)} samples")

    X = np.vstack(all_embeddings)
    y = np.array(all_labels)
    print(f"Total: {len(y)} samples, embedding shape: {X.shape}")

    return X, y, SUPERGLUE_TASKS
