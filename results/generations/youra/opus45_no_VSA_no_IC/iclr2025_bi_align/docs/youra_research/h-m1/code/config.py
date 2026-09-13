"""H-M1 Configuration - Semantic Similarity Analysis."""

from pathlib import Path


CONFIG = {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "batch_size": 64,
    "h_e1_output_dir": Path(__file__).parent.parent.parent / "h-e1" / "code" / "outputs",
    "h_e1_code_dir": Path(__file__).parent.parent.parent / "h-e1" / "code",
    "output_dir": Path(__file__).parent / "outputs",
    "bootstrap_samples": 10000,
    "seed": 42,
    "min_samples_per_mode": 500,
    "modes": [1, 3],
}
