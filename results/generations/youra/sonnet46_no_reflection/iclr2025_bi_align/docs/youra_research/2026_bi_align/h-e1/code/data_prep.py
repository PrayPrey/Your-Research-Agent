"""
data_prep.py — H-E1: AIFS feature extraction, clustering, and pair construction.
"""
import re
import numpy as np
import pandas as pd
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Constants (C-E1-1)
# ---------------------------------------------------------------------------
AIFS_PATTERNS: dict[str, re.Pattern] = {
    "structured_list": re.compile(r"^\s*(\d+\.|\*|-)\s", re.MULTILINE),
    "safety_preface": re.compile(
        r"\b(I (cannot|should not|must not)|please note|important:)\b",
        re.IGNORECASE,
    ),
    "cot_marker": re.compile(
        r"\b(step \d+|first,|second,|finally,|let('s| us))\b",
        re.IGNORECASE,
    ),
    "hedging": re.compile(
        r"\b(however,|that said,|it depends|on the other hand)\b",
        re.IGNORECASE,
    ),
}

COSINE_THRESHOLD: float = 0.85
MIN_TOKEN_COUNT: int = 20
MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
MAX_SEQ_LENGTH: int = 256
BATCH_SIZE: int = 512
RANDOM_SEED: int = 1

DATASET_NAME: str = "Anthropic/hh-rlhf"
SPLIT_BASE_DIR: str = "helpful-base"
SPLIT_ONLINE_DIR: str = "helpful-online"
LABEL_BASE: int = 0
LABEL_ONLINE: int = 1


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------

def load_hh_rlhf() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load Anthropic/hh-rlhf helpful-base and helpful-online splits.
    Returns (df_base, df_online) each with columns: [chosen, rejected].
    """
    ds_base = load_dataset(DATASET_NAME, data_dir=SPLIT_BASE_DIR, split="train", verification_mode="no_checks")
    ds_online = load_dataset(DATASET_NAME, data_dir=SPLIT_ONLINE_DIR, split="train", verification_mode="no_checks")
    df_base = ds_base.to_pandas()[["chosen", "rejected"]]  # type: ignore[union-attr,return-value]
    df_online = ds_online.to_pandas()[["chosen", "rejected"]]  # type: ignore[union-attr,return-value]
    return df_base, df_online  # type: ignore[return-value]


def extract_dialogue(example: dict) -> dict:
    """TRL common-prefix pattern: strip shared prefix to get {prompt, chosen, rejected}."""
    chosen = example["chosen"]
    rejected = example["rejected"]
    # Find longest common prefix character by character
    min_len = min(len(chosen), len(rejected))
    prefix_len = 0
    for i in range(min_len):
        if chosen[i] == rejected[i]:
            prefix_len = i + 1
        else:
            break
    prefix = chosen[:prefix_len]
    # Trim prefix to last "\n\nAssistant: " boundary
    marker = "\n\nAssistant: "
    idx = prefix.rfind(marker)
    if idx != -1:
        prefix = prefix[: idx + len(marker)]
    chosen_text = chosen[len(prefix):]
    rejected_text = rejected[len(prefix):]
    return {"prompt": prefix, "chosen": chosen_text, "rejected": rejected_text}


def filter_pairs(df: pd.DataFrame, min_tokens: int = MIN_TOKEN_COUNT) -> pd.DataFrame:
    """Keep rows where both chosen and rejected have >= min_tokens whitespace-split tokens."""
    mask = (
        df["chosen"].str.split().str.len() >= min_tokens
    ) & (
        df["rejected"].str.split().str.len() >= min_tokens
    )
    return df[mask].reset_index(drop=True)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# AIFS Feature Extraction (L-2-1)
# ---------------------------------------------------------------------------

def compute_aifs_score(text: str) -> float:
    """AIFS density: total pattern matches / (token_count / 100). Returns float >= 0."""
    token_count = max(1, len(text.split()))
    hits = sum(len(p.findall(text)) for p in AIFS_PATTERNS.values())
    return hits / (token_count / 100)


# ---------------------------------------------------------------------------
# Clustering (L-2-2)
# ---------------------------------------------------------------------------

def cluster_prompts(
    prompts: list[str],
    threshold: float = COSINE_THRESHOLD,
    batch_size: int = BATCH_SIZE,
) -> np.ndarray:
    """Cluster prompts via all-MiniLM-L6-v2 embeddings + cosine distance AgglomerativeClustering.
    Returns cluster_id array of shape [len(prompts),] with int cluster IDs.
    Uses sklearn AgglomerativeClustering for scalable O(N log N) clustering.
    """
    from sklearn.cluster import AgglomerativeClustering

    encoder = SentenceTransformer(MODEL_NAME)
    encoder.max_seq_length = MAX_SEQ_LENGTH
    embeddings = encoder.encode(
        prompts,
        batch_size=batch_size,
        show_progress_bar=len(prompts) > 1000,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    # Convert cosine threshold to distance cutoff: cosine_dist = 1 - cosine_sim
    distance_threshold = 1.0 - threshold  # e.g., 0.85 threshold → 0.15 distance

    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="cosine",
        linkage="average",
    )
    cluster_ids = clustering.fit_predict(embeddings).astype(int)
    return cluster_ids


def validate_clusters(df_pairs: pd.DataFrame) -> None:
    """Abort if fewer than 100 clusters contain >= 2 pairs. Raises ValueError."""
    # Each pair creates 2 rows (chosen=1 and chosen=0), so divide by 2 for pair count
    row_counts = df_pairs.groupby("cluster_id").size()
    pair_counts = row_counts // 2  # convert row count to pair count
    valid = int((pair_counts >= 2).sum())
    if valid < 100:
        raise ValueError(
            f"Only {valid} valid clusters with >= 2 pairs; need >= 100 for ConditionalLogit."
        )


# ---------------------------------------------------------------------------
# Pair Construction (L-2-1 continued)
# ---------------------------------------------------------------------------

def build_pairs_df(
    df_base: pd.DataFrame,
    df_online: pd.DataFrame,
    cluster_ids: np.ndarray,
) -> pd.DataFrame:
    """Construct analysis-ready pairs DataFrame.
    Returns DataFrame with columns:
      chosen          int       {0, 1}
      delta_aifs      float     aifs(chosen) - aifs(rejected)
      delta_length    float     token count diff (chosen - rejected)
      delta_aifs_x_split float  delta_aifs * split
      split           int       {0=base, 1=online}
      cluster_id      int       semantic cluster assignment
    """
    records = []
    base_len = len(df_base)
    online_len = len(df_online)
    total_len = base_len + online_len
    assert len(cluster_ids) == total_len, (
        f"cluster_ids length {len(cluster_ids)} != total rows {total_len}"
    )

    for split_label, df, offset in [
        (LABEL_BASE, df_base, 0),
        (LABEL_ONLINE, df_online, base_len),
    ]:
        for row_i, (_, row) in enumerate(df.iterrows()):
            chosen_text = row["chosen"]
            rejected_text = row["rejected"]
            cid = int(cluster_ids[offset + row_i])

            aifs_chosen = compute_aifs_score(chosen_text)
            aifs_rejected = compute_aifs_score(rejected_text)
            len_chosen = len(chosen_text.split())
            len_rejected = len(rejected_text.split())

            delta_aifs = aifs_chosen - aifs_rejected
            delta_length = float(len_chosen - len_rejected)
            delta_aifs_x_split = delta_aifs * split_label

            # ConditionalLogit requires two rows per pair (chosen=1 and chosen=0)
            records.append({
                "chosen": 1,
                "delta_aifs": delta_aifs,
                "delta_length": delta_length,
                "delta_aifs_x_split": delta_aifs_x_split,
                "split": split_label,
                "cluster_id": cid,
            })
            records.append({
                "chosen": 0,
                "delta_aifs": -delta_aifs,
                "delta_length": -delta_length,
                "delta_aifs_x_split": -delta_aifs_x_split,
                "split": split_label,
                "cluster_id": cid,
            })

    df_pairs = pd.DataFrame(records)
    return df_pairs
