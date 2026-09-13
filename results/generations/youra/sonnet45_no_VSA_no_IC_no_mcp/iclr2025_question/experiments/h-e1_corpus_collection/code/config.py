"""Configuration for retrospective corpus collection."""

CONFIG = {
    "collection": {
        "pwc_api_url": "https://paperswithcode.com/api/v1/papers",
        "pwc_tag": "ablation",
        "pwc_max_results": 50,

        "conferences": [
            {"venue": "NeurIPS", "years": [2020, 2021, 2022, 2023, 2024]},
            {"venue": "ICML", "years": [2020, 2021, 2022, 2023, 2024]},
            {"venue": "ICLR", "years": [2020, 2021, 2022, 2023, 2024]},
        ],

        "keywords": ["ablation study", "overhead", "sample size"],
        "max_retries": 3,
        "timeout_seconds": 30,
    },

    "extraction": {
        "timing_patterns": [
            r"Table\s+\d+:.*overhead.*sample.*\n(.*?\n){1,10}",
            r"(\d+)\s*samples?:\s*(\d+\.?\d*)\s*sec.*?(\d+)\s*samples?:\s*(\d+\.?\d*)\s*sec",
            r"micro-pilot.*?(\d+\.?\d*)\s*sec.*?full.*?(\d+\.?\d*)\s*sec",
            r"ablation.*?\n.*?(\d+)\s+(\d+\.?\d*).*?\n.*?(\d+)\s+(\d+\.?\d*)",
        ],
        "micro_pilot_threshold": 50,
        "full_scale_threshold": 1000,
        "sample_size_ratio_min": 10,
    },

    "validation": {
        "target_count": 30,
        "pass_threshold": 30,
        "fail_threshold": 20,
        "stratification": {
            "low_overhead_max": 20.0,
            "high_overhead_min": 80.0,
            "cv_threshold": 0.5,
        },
        "spot_check_rate": 0.2,
    },

    "paths": {
        "corpus_output": "data/retrospective_corpus/papers_metadata.json",
        "raw_papers_dir": "data/retrospective_corpus/raw_papers",
        "checkpoints_dir": "data/retrospective_corpus/checkpoints",
        "validation_report": "data/retrospective_corpus/validation_report.md",
    },

    "seed": 42,
}
