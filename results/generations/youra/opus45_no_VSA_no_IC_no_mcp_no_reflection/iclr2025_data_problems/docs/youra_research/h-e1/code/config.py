"""Configuration for h-e1 experiment."""

CONFIG = {
    # Data
    "domains": ['pile-cc', 'wikipedia', 'github', 'arxiv',
                'stackexchange', 'pubmed', 'books3', 'openwebtext2'],
    "samples_per_domain": 1000,
    "max_tokens": 512,
    "pile_source": "monology/pile-uncopyrighted",
    "mmlu_source": "cais/mmlu",
    "data_dir": "data/h-e1",

    # Model
    "model_name": "intfloat/e5-large-v2",
    "embed_dim": 1024,
    "passage_prefix": "passage: ",
    "query_prefix": "query: ",
    "batch_size": 32,

    # Reproducibility
    "seeds": [42, 43, 44],

    # Output paths
    "domain_emb_path": "embeddings/domain_emb.pt",
    "task_emb_path": "embeddings/task_emb.pt",
    "similarities_path": "results/similarities.csv",
    "domain_scores_path": "results/domain_scores.json",
    "report_path": "results/h-e1_analysis.md",
    "figure_path": "figures/domain_similarity_bar.png",

    # Success thresholds (from PRD)
    "min_cross_domain_std": 0.05,
    "max_reproducibility_variance": 0.05,
    "anova_p_threshold": 0.05,
}
