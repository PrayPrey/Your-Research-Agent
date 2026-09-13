"""Configuration for H-E1 experiment."""

CONFIG = {
    # data
    "dataset": "glue/sst2",
    "noise_rate": 0.05,
    "noise_seed": 42,
    "max_length": 128,

    # models
    "bert_name": "bert-base-uncased",
    "gpt2_name": "gpt2",
    "num_labels": 2,

    # training
    "lr": 2e-5,
    "epochs": 3,
    "batch_size": 32,
    "seeds": [42, 43, 44, 45, 46],

    # attribution
    "methods": ["trak", "ekfac", "tracin"],
    "architectures": ["bert", "gpt2"],

    # stats
    "alpha": 0.05,
    "min_auc_diff": 0.05,
    "min_effect_size": 0.3,

    # paths
    "checkpoint_dir": "checkpoints/",
    "figures_dir": "figures/",
    "results_path": "results.json",
}
