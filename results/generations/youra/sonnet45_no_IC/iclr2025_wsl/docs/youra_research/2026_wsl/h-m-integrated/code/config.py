# config.py - Configuration for H-M-Integrated CAPE Experiment

CONFIG = {
    # Global settings
    "hypothesis_id": "H-M-Integrated",
    "random_seed": 42,

    # Model Zoo Collection (FR-1)
    "model_zoo": {
        "n_per_architecture": 100,
        "architectures": ["resnet50", "vit_base_patch16_224",
                         "mobilenetv2_100", "efficientnet_b0"],
        "dataset_filter": "imagenet-1k",
        "retry_attempts": 3,
        "min_success_rate": 0.90,
        "cache_dir": "data/raw/models/"
    },

    # Data Preprocessing (FR-1)
    "preprocessing": {
        "normalization": "frobenius",
        "operation_grouping": True,
        "cache_preprocessed": True,
        "preprocessed_dir": "data/preprocessed/"
    },

    # Architecture DAG (FR-1, FR-5)
    "architecture_dag": {
        "d_arch": 64,
        "include_layer_types": True,
        "include_dimensions": True,
        "save_graphs": True,
        "graph_dir": "data/preprocessed/arch_graphs/"
    },

    # Train/Val/Test Split (FR-1)
    "data_split": {
        "train_ratio": 0.70,
        "val_ratio": 0.15,
        "test_ratio": 0.15,
        "stratify_by_architecture": True,
        "random_state": 42
    },

    # DataLoader Settings
    "dataloader": {
        "num_workers": 4,
        "pin_memory": True,
        "persistent_workers": True,
        "prefetch_factor": 2
    },

    # CAPE Encoder Architecture (FR-3, FR-4, FR-5, FR-6)
    "cape_encoder": {
        "d_z": 256,
        "d_arch": 64,
        "tau": 0.07,
        "dropout": 0.1,
        "num_gnn_layers": 3,
        "alpha_init": 0.5,
        "projector_hidden_dim": 256,
        "gnn_hidden_dim": 128,
        "operation_types": ["conv", "attention", "mlp"]
    },

    # Operation-Specific Encoders (FR-3)
    "operation_encoders": {
        "sane_conv": {
            "spatial_tokenize": True,
            "output_dim": 256,
            "pooling": "mean"
        },
        "unf_attention": {
            "equivariant_process": True,
            "output_dim": 256,
            "pooling": "mean"
        },
        "mlp_encoder": {
            "set_encoding": True,
            "output_dim": 256,
            "pooling": "mean"
        }
    },

    # Training Hyperparameters (FR-6)
    "training": {
        "batch_size": 32,
        "epochs": 100,
        "optimizer": {
            "name": "adamw",
            "lr": 1e-4,
            "weight_decay": 1e-4,
            "betas": [0.9, 0.999],
            "eps": 1e-8
        },
        "scheduler": {
            "name": "cosine",
            "warmup_ratio": 0.10,
            "min_lr": 1e-7
        },
        "early_stopping": {
            "patience": 10,
            "metric": "val_combined_loss",
            "mode": "min"
        },
        "mixed_precision": True,
        "gradient_clip_norm": 1.0,
        "checkpoint_frequency": 10
    },

    # Loss Function (FR-6)
    "loss": {
        "lambda_contrast": 1.0,
        "lambda_property": 0.5,
        "contrastive_temperature": 0.07
    },

    # Ablation Study (FR-7)
    "ablation": {
        "variants": {
            "sne_baseline": {
                "enable_operation_encoders": False,
                "enable_contrastive": False,
                "enable_gnn": False,
                "model_class": "SNEBaseline"
            },
            "operation_only": {
                "enable_operation_encoders": True,
                "enable_contrastive": False,
                "enable_gnn": False,
                "model_class": "CAPEEncoder"
            },
            "op_contrastive": {
                "enable_operation_encoders": True,
                "enable_contrastive": True,
                "enable_gnn": False,
                "model_class": "CAPEEncoder"
            },
            "full_cape": {
                "enable_operation_encoders": True,
                "enable_contrastive": True,
                "enable_gnn": True,
                "model_class": "CAPEEncoder"
            }
        },
        "identical_hyperparameters": True,
        "checkpoint_prefix_by_variant": True
    },

    # Cross-Architecture Evaluation (FR-8)
    "evaluation": {
        "primary_transfer": {
            "source": "resnet50",
            "target": "vit_base_patch16_224"
        },
        "n_permutations": 1000,
        "alpha": 0.05,
        "compute_all_pairs": True,
        "metric": "spearman"
    },

    # Diagnostic Thresholds (FR-9)
    "diagnostics": {
        "operation_similarity": {
            "threshold": 0.95,
            "target": 0.80,
            "pairs": [["conv", "attention"], ["conv", "mlp"], ["attention", "mlp"]]
        },
        "intra_arch_variance": {
            "threshold": 0.1,
            "target": 0.15
        },
        "gnn_weight": {
            "threshold": 0.1,
            "target": 0.3,
            "check_performance_gain": True
        }
    },

    # Success Criteria
    "success_criteria": {
        "target_rho": 0.65,
        "baseline_rho": 0.54,
        "min_improvement": 0.10,
        "p_value_threshold": 0.05
    },

    # Visualization (FR-10)
    "visualization": {
        "dpi": 300,
        "style": "seaborn",
        "output_dir": "figures/",
        "formats": ["png", "pdf"],
        "plots": {
            "gate_comparison": {
                "figsize": [10, 6],
                "include_thresholds": True,
                "metrics": ["rho_cape", "rho_sne", "rho_delta",
                           "diag1_sim", "diag2_var", "diag3_alpha"]
            },
            "transfer_matrix": {
                "figsize": [10, 8],
                "cmap": "viridis",
                "annot": True
            },
            "ablation_bars": {
                "figsize": [8, 6],
                "show_error_bars": False
            },
            "embedding_space": {
                "method": "umap",
                "n_components": 2,
                "figsize": [10, 8]
            }
        }
    },

    # Directories
    "directories": {
        "hypothesis_root": "docs/youra_research/h-m-integrated",
        "data": "data/",
        "raw": "data/raw/",
        "preprocessed": "data/preprocessed/",
        "splits": "data/splits/",
        "checkpoints": "checkpoints/",
        "results": "results/",
        "figures": "figures/",
        "logs": "logs/"
    }
}
