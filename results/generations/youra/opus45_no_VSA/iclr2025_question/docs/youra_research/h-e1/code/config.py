# config.py - h-e1 NTI EXISTENCE PoC
import os

CONFIG = {
    "seed": 42,
    "model_id": "meta-llama/Llama-2-7b-hf",
    "device": "cuda",
    "dtype": "float16",
    "target_layers": (24, 31),  # inclusive, LLaMA-2-7B has layers 0-31
    "n_folds": 5,
    "auroc_threshold": 0.55,
    "min_fold_threshold": 0.52,
    "min_pass_rate": 0.8,
    "dataset": "truthful_qa",
    "dataset_config": "multiple_choice",
    "figures_dir": os.path.join(os.path.dirname(__file__), "figures"),
    "outputs_dir": os.path.join(os.path.dirname(__file__), "outputs"),
    "batch_size": 4,  # conservative for 7B model
}
