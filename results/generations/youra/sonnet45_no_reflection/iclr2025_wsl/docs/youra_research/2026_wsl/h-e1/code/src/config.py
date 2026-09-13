"""Configuration for H-E1 Quotient Space Existence"""

DATASET_CONFIG = {
    "cache_dir": "./data/model_zoo",
    "architectures": ["CNN", "Transformer", "RNN"],
    "size_range": (10_000_000, 100_000_000),
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,
    "normalize_per_layer": True,
    "max_weight_dim": 100_000,
    "batch_size": 32,
    "num_workers": 4,
    "pin_memory": True
}

BASELINE_CONFIG = {
    "weight_dim": 100_000,
    "hidden_dim": 128,
    "output_dim": 32,
    "encoder_layers": [512, 256, 128],
    "encoder_activation": "relu",
    "decoder_layers": [128, 256],
    "decoder_activation": "relu",
    "reconstruct_layers": [256, 512, 100_000],
    "aggregation": "sum"
}

PROPOSED_CONFIG = {
    "weight_dim": 100_000,
    "K": 32,
    "hidden_dim": 256,
    "num_arch_classes": 3,
    "arch_embed_dim": 64,
    "encoder_layers": [256, 128],
    "encoder_activation": "relu",
    "use_layer_norm": True,
    "decoder_layers": [128, 256],
    "decoder_activation": "relu",
    "reconstruct_layers": [256, 512, 100_000],
    "aggregation": "mean"
}

TRAINING_CONFIG = {
    "optimizer": "adam",
    "learning_rate": 1e-3,
    "betas": (0.9, 0.999),
    "weight_decay": 1e-4,
    "scheduler": "cosine_annealing",
    "T_max": 100,
    "num_epochs": 100,
    "batch_size": 32,
    "lambda_equiv": 0.5,
    "patience": 10,
    "min_delta": 1e-4,
    "checkpoint_dir": "./checkpoints",
    "save_best_only": True,
    "seed": 42,
    "deterministic": True
}

EVALUATION_CONFIG = {
    "num_permutations": 1000,
    "divergence_threshold": 0.01,
    "target_reconstruction_error": 10.0,
    "target_frozen_k_gen": 10.0,
    "target_kernel_robustness": 90.0,
    "frozen_k_train_archs": ["CNN", "Transformer"],
    "frozen_k_test_arch": "RNN",
    "results_dir": "./results",
    "metrics_file": "metrics.csv"
}

ABLATION_CONFIG = {
    "lambda_equiv_values": [0.0, 0.25, 0.5, 0.75, 1.0],
    "K_values": [16, 32, 64],
    "ablation_results_dir": "./results/ablations",
    "save_all_checkpoints": False
}

VISUALIZATION_CONFIG = {
    "figures_dir": "./figures",
    "dpi": 300,
    "format": "png",
    "tsne_perplexity": 30,
    "tsne_n_iter": 1000,
    "random_state": 42,
    "figsize": (10, 6),
    "colors": {
        "CNN": "blue",
        "Transformer": "orange",
        "RNN": "green"
    },
    "gate_metrics_names": [
        "Reconstruction Error (%)",
        "Frozen-K Generalization (%)",
        "Kernel Robustness (%)"
    ]
}
