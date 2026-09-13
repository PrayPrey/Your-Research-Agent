"""
Data utilities for EmbedPrint experiments.
"""
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from datasets import load_dataset
from sklearn.cluster import MiniBatchKMeans
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttributionDataset(Dataset):
    """Dataset with cluster assignments for attribution."""

    def __init__(
        self,
        texts: List[str],
        tokenizer,
        max_length: int = 128,
        cluster_ids: Optional[np.ndarray] = None,
        is_canary: Optional[np.ndarray] = None,
    ):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.cluster_ids = cluster_ids if cluster_ids is not None else np.zeros(len(texts), dtype=np.int64)
        self.is_canary = is_canary if is_canary is not None else np.zeros(len(texts), dtype=bool)

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "cluster_id": torch.tensor(self.cluster_ids[idx], dtype=torch.long),
            "is_canary": torch.tensor(self.is_canary[idx], dtype=torch.bool),
            "idx": torch.tensor(idx, dtype=torch.long),
        }


def load_and_prepare_data(config) -> Tuple[List[str], List[str]]:
    """Load dataset and prepare train/eval splits."""
    logger.info(f"Loading dataset: {config.dataset_name}")

    dataset = load_dataset(config.dataset_name, config.dataset_config, trust_remote_code=True)

    # Get texts from training set
    train_texts = []
    for item in dataset["train"]:
        text = item["text"].strip()
        if len(text) > 50:  # Filter very short texts
            train_texts.append(text)
        if len(train_texts) >= config.num_train_samples:
            break

    # Get texts from validation set
    eval_texts = []
    for item in dataset["validation"]:
        text = item["text"].strip()
        if len(text) > 50:
            eval_texts.append(text)
        if len(eval_texts) >= config.num_eval_samples:
            break

    logger.info(f"Loaded {len(train_texts)} training samples and {len(eval_texts)} eval samples")
    return train_texts, eval_texts


def create_canary_samples(base_texts: List[str], num_canaries: int, seed: int = 42) -> Tuple[List[str], np.ndarray]:
    """Create distinctive canary samples for evaluation."""
    np.random.seed(seed)

    canary_prefixes = [
        "CANARY_MARKER_UNIQUE: ",
        "SPECIAL_ATTRIBUTION_TEST: ",
        "FINGERPRINT_EVAL_SAMPLE: ",
    ]

    # Mark some samples as canaries by adding distinctive prefixes
    is_canary = np.zeros(len(base_texts), dtype=bool)
    canary_indices = np.random.choice(len(base_texts), min(num_canaries, len(base_texts)), replace=False)

    modified_texts = base_texts.copy()
    for i, idx in enumerate(canary_indices):
        prefix = canary_prefixes[i % len(canary_prefixes)]
        modified_texts[idx] = prefix + modified_texts[idx]
        is_canary[idx] = True

    logger.info(f"Created {is_canary.sum()} canary samples")
    return modified_texts, is_canary


def cluster_texts(
    texts: List[str],
    num_coarse: int,
    num_fine_per_coarse: int,
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    device: str = "cuda",
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Perform hierarchical clustering on texts.
    Returns coarse cluster ids, fine cluster ids, and embeddings.
    """
    logger.info("Computing text embeddings for clustering...")
    embed_model = SentenceTransformer(embedding_model_name, device=device)
    embeddings = embed_model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Normalize embeddings
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    # Coarse clustering
    logger.info(f"Performing coarse clustering into {num_coarse} clusters...")
    coarse_kmeans = MiniBatchKMeans(n_clusters=num_coarse, random_state=42, batch_size=256)
    coarse_labels = coarse_kmeans.fit_predict(embeddings)

    # Fine clustering within each coarse cluster
    logger.info(f"Performing fine clustering ({num_fine_per_coarse} per coarse cluster)...")
    fine_labels = np.zeros_like(coarse_labels)

    for coarse_id in range(num_coarse):
        mask = coarse_labels == coarse_id
        if mask.sum() < num_fine_per_coarse:
            # If cluster is too small, use identity mapping
            fine_labels[mask] = np.arange(mask.sum())
        else:
            cluster_embeddings = embeddings[mask]
            fine_kmeans = MiniBatchKMeans(
                n_clusters=num_fine_per_coarse, random_state=42, batch_size=min(256, mask.sum())
            )
            fine_labels[mask] = fine_kmeans.fit_predict(cluster_embeddings)

    # Compute global cluster id
    total_clusters = num_coarse * num_fine_per_coarse
    global_cluster_ids = coarse_labels * num_fine_per_coarse + fine_labels
    global_cluster_ids = np.clip(global_cluster_ids, 0, total_clusters - 1)

    logger.info(f"Clustering complete. {len(np.unique(global_cluster_ids))} unique clusters.")
    return global_cluster_ids, coarse_labels, embeddings


def create_dataloaders(
    config,
    train_texts: List[str],
    eval_texts: List[str],
    cluster_ids: np.ndarray,
    is_canary: np.ndarray,
    tokenizer,
) -> Tuple[DataLoader, DataLoader]:
    """Create train and eval dataloaders."""

    train_dataset = AttributionDataset(
        texts=train_texts,
        tokenizer=tokenizer,
        max_length=config.max_seq_length,
        cluster_ids=cluster_ids,
        is_canary=is_canary,
    )

    # For eval, we don't have cluster assignments
    eval_dataset = AttributionDataset(
        texts=eval_texts,
        tokenizer=tokenizer,
        max_length=config.max_seq_length,
        cluster_ids=np.zeros(len(eval_texts), dtype=np.int64),
        is_canary=np.zeros(len(eval_texts), dtype=bool),
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=True,
    )

    eval_loader = DataLoader(
        eval_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=True,
    )

    return train_loader, eval_loader
