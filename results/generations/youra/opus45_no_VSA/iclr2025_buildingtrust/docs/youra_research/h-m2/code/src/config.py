CONFIG = {
    "seed": 42,
    "decode_temperature": 0.0,
    "few_shot_k": 3,
    "benchmarks": ["truthfulqa", "mmlu", "advglue", "bbh", "gsm8k", "winogrande"],
    "n_pairs_expected": 16,
    "paws_wiki_path": "../data/paws_wiki_test.json",
    "paws_qqp_path": "../data/paws_qqp_dev.json",
    "model_pairs_path": "../data/model_pairs.yaml",
    "results_dir": "../results/",
    "alpha": 0.05,
}
