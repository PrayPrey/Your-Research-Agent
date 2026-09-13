from __future__ import annotations
from pathlib import Path

MODEL_SIZES: list[str] = ["70m", "1b", "6.9b"]

MODEL_IDS: dict[str, str] = {
    "70m": "EleutherAI/pythia-70m",
    "1b": "EleutherAI/pythia-1b",
    "6.9b": "EleutherAI/pythia-6.9b",
}

CHECKPOINT_STEPS: list[int] = [
    0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
    1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000,
    11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000, 20000,
    21000, 22000, 23000, 24000, 25000, 26000, 27000, 28000, 29000, 30000,
    31000, 32000, 33000, 34000, 35000, 36000, 37000, 38000, 39000, 40000,
    41000, 42000, 43000, 44000, 45000, 46000, 47000, 48000, 49000, 50000,
    51000, 52000, 53000, 54000, 55000, 56000, 57000, 58000, 59000, 60000,
    61000, 62000, 63000, 64000, 65000, 66000, 67000, 68000, 69000, 70000,
    71000, 72000, 73000, 74000, 75000, 76000, 77000, 78000, 79000, 80000,
    81000, 82000, 83000, 84000, 85000, 86000, 87000, 88000, 89000, 90000,
    91000, 92000, 93000, 94000, 95000, 96000, 97000, 98000, 99000, 100000,
    101000, 102000, 103000, 104000, 105000, 106000, 107000, 108000, 109000, 110000,
    111000, 112000, 113000, 114000, 115000, 116000, 117000, 118000, 119000, 120000,
    121000, 122000, 123000, 124000, 125000, 126000, 127000, 128000, 129000, 130000,
    131000, 132000, 133000, 134000, 135000, 136000, 137000, 138000, 139000, 140000,
    141000, 142000, 143000,
]  # len=154

PILE_DOMAINS: list[str] = [
    "Pile-CC",
    "PubMed Central",
    "Books3",
    "OpenWebText2",
    "ArXiv",
    "Github",
    "FreeLaw",
    "StackExchange",
    "USPTO Backgrounds",
    "PubMed Abstracts",
    "Gutenberg (PG-19)",
    "OpenSubtitles",
    "Wikipedia (en)",
    "DM Mathematics",
    "Ubuntu IRC",
    "BookCorpus2",
    "EuroParl",
    "HackerNews",
    "YoutubeSubtitles",
    "PhilPapers",
    "NIH ExPorter",
    "Enron Emails",
]  # len=22

FOCAL_DOMAINS: dict[str, str] = {
    "wikipedia": "Wikipedia (en)",
    "books": "Books3",
}

TASKS: dict[str, dict] = {
    "mmlu": {"num_fewshot": 5, "metric": "acc,none"},
    "hellaswag": {"num_fewshot": 10, "metric": "acc_norm,none"},
}

BATCH_SIZE: str = "auto"
DTYPE: str = "float"

FLOOR_THRESHOLD: float = 0.20  # lowered from 0.30: Pythia-70m MMLU peaks at 0.23 (never exceeds 0.30)
MIN_VALID_CHECKPOINTS: int = 100

FISHER_ALPHA: float = 0.10
N_FOCAL_COMPARISONS: int = 4

NGRAM_SIZE: int = 13
CONTAMINATION_DELTA_THRESHOLD: float = 0.03

H_E1_EXPOSURE_DIR: str = "docs/youra_research/h-e1"
RESULTS_DIR: str = "results/h-m2"
EVAL_CACHE_DIR: str = "results/h-m2/eval_cache"
FIGURES_DIR: str = "docs/youra_research/h-m2/figures"

SEED: int = 42
