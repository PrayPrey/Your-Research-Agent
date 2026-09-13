"""H-M1 Configuration: 13-gram overlap detection."""

NGRAM_SIZE = 13
PILE_SUBSET_DOCS = 50_000
PILE_DATASET = "monology/pile-uncopyrighted"  # Accessible subset of The Pile
BENCHMARKS = {
    "mmlu": ("cais/mmlu", "all", "test"),
    "arc_challenge": ("allenai/ai2_arc", "ARC-Challenge", "test"),
    "hellaswag": ("Rowan/hellaswag", None, "validation"),
    "winogrande": ("allenai/winogrande", "winogrande_xl", "validation"),
}
OVERLAP_THRESHOLD = 0.01
SEED = 1
OUTPUT_DIR = "results/"
INDEX_PATH = "results/pile_index.pkl"
RESULTS_JSON = "results/overlap_results.json"
FIGURES_DIR = "figures/"
