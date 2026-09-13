"""Configuration for h-m2: Error Type Signature Analysis."""

CONFIG = {
    # ===== DATASETS (NEW) =====
    # NaturalQuestions - Knowledge Gaps
    "dataset_nq": {
        "name": "natural_questions",
        "split": "validation",
        "num_samples": 100,
        "error_type": "knowledge_gaps"
    },

    # TruthfulQA - Confident Misconceptions
    "dataset_tqa": {
        "name": "truthful_qa",
        "config": "generation",
        "split": "validation",
        "num_samples": 100,
        "error_type": "confident_misconceptions"
    },

    # ===== MODEL (INHERITED FROM h-m1) =====
    "model_name": "mistralai/Mistral-7B-v0.1",
    "device": "cuda",
    "dtype": "float16",

    # ===== GENERATION (OPTIMIZED FROM h-m1) =====
    "k_samples": 5,  # Optimized from K=10 in h-m1 validation
    "temperature": 0.7,
    "max_new_tokens": 50,

    # ===== UNCERTAINTY METHODS (REUSED FROM h-m1) =====
    "embedding_model": "all-MiniLM-L6-v2",
    "clustering_threshold": 0.5,

    # ===== STATISTICAL ANALYSIS (NEW) =====
    "significance_threshold": 0.05,  # p-value for t-test

    # ===== EXPERIMENT =====
    "seed": 42,
    "output_dir": "./results",
    "figures_dir": "./figures",

    # ===== BASE HYPOTHESIS INTEGRATION (NEW) =====
    "h_m1_code_path": "/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_question_3/docs/youra_research/20260421_question/h-m1/code",  # For sys.path reuse
}
