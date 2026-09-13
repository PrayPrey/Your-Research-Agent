"""Generate embeddings with early/mid/late models."""
import numpy as np
import time
from sentence_transformers import SentenceTransformer
from typing import List
import yaml


def load_config(config_path: str = "config/experiment_config.yaml") -> dict:
    """Load experiment config."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def generate_embeddings(
    model_id: str,
    texts: List[str],
    batch_size: int = 32,
    device: str = "cuda",
    task_instruction: str = None
) -> tuple[np.ndarray, float]:
    """
    Generate embeddings for corpus.
    Returns: (embeddings [N, D], compute_time in seconds)
    """
    print(f"\nLoading model: {model_id}")
    model = SentenceTransformer(model_id, device=device)

    print(f"Encoding {len(texts)} samples (batch_size={batch_size})...")
    start = time.time()

    if task_instruction and "instructor" in model_id.lower():
        # Instructor models use task instructions
        embeddings = model.encode(
            [[task_instruction, text] for text in texts],
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
    else:
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )

    compute_time = time.time() - start

    print(f"✓ Generated embeddings: shape={embeddings.shape}, time={compute_time:.2f}s")

    return embeddings, compute_time


def save_embeddings(embeddings: np.ndarray, path: str) -> None:
    """Save embeddings to .npy file."""
    np.save(path, embeddings)
    print(f"✓ Saved embeddings to {path}")


def generate_all_embeddings(texts: List[str], config: dict) -> dict:
    """
    Generate early/mid/late embeddings.
    Returns: {stage: (embeddings_path, compute_time)}
    """
    results = {}

    for stage in ["early", "mid", "late"]:
        model_config = config["embedding_models"][stage]
        model_id = model_config["model_id"]
        task_instruction = model_config.get("task_instruction")

        embeddings, compute_time = generate_embeddings(
            model_id=model_id,
            texts=texts,
            task_instruction=task_instruction
        )

        output_path = f"{config['paths']['embeddings_dir']}{stage}_embeddings.npy"
        save_embeddings(embeddings, output_path)

        results[stage] = {
            "path": output_path,
            "time": compute_time,
            "shape": embeddings.shape
        }

    return results


if __name__ == "__main__":
    from load_data import load_and_format_dolly

    config = load_config()
    _, texts = load_and_format_dolly(config["dataset"]["cache_dir"])

    results = generate_all_embeddings(texts, config)

    print("\n=== Embedding Generation Summary ===")
    for stage, info in results.items():
        print(f"{stage:5s}: {info['shape']} in {info['time']:.2f}s")

    print(f"\n✓ All embeddings generated")
