# config.py - h-m3 RCI Flip Pattern Detection (MECHANISM)
import os
import random
import torch
import numpy as np

CONFIG = {
    "seed": 42,
    "model_id": "meta-llama/Llama-2-7b-hf",
    "device": "cuda",
    "dtype": "float16",
    "layer_range": (24, 32),  # inclusive, 9 layers for RCI analysis
    "batch_size": 1,  # single sample for hidden state extraction
    "temperature": 0.0,  # greedy decode for hallucination labeling
    "dataset": "truthful_qa",
    "dataset_config": "multiple_choice",
    "n_samples": 817,  # full TruthfulQA MC1
    # Gate thresholds
    "halluc_rate_threshold": 0.30,
    "correct_rate_threshold": 0.10,
    "separation_threshold": 0.20,
    # Falsification boundaries
    "halluc_falsification": 0.20,
    "correct_falsification": 0.15,
    "figures_dir": os.path.join(os.path.dirname(__file__), "figures"),
    "outputs_dir": os.path.join(os.path.dirname(__file__), "outputs"),
}

def set_seed(seed=None):
    seed = seed or CONFIG["seed"]
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
