"""
H-E1 Experiment Configuration
Corpus statistical analysis - no model training needed.
"""

CONFIG = {
    # Experiment settings
    "seed": 42,
    "n_docs": 10_000_000,
    "window_size": 10,
    "n_bootstrap": 10_000,
    "gate_threshold_pct": 5.0,

    # Dataset / model identifiers
    "fasttext_model_id": "mlfoundations/fasttext-oh-eli5",
    "dataset_id": "mlfoundations/dclm-baseline-1.0",
    "fasttext_score_field": "fasttext_openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train_prob",

    # Filter configurations: (name, filter_type, percentile_threshold)
    # percentile_threshold=None means no percentile filter (doremi or unfiltered)
    "configurations": [
        {"id": "C0", "filter_type": "unfiltered",  "percentile": 0},
        {"id": "C1", "filter_type": "fasttext",     "percentile": 10},
        {"id": "C2", "filter_type": "fasttext",     "percentile": 30},
        {"id": "C3", "filter_type": "fasttext",     "percentile": 50},
        {"id": "C4", "filter_type": "fasttext",     "percentile": 70},
        {"id": "C5", "filter_type": "fasttext",     "percentile": 90},
        {"id": "C6", "filter_type": "doremi",       "percentile": None},
    ],

    # WinoBias 60-occupation lexicon
    "occupation_lexicon": [
        "nurse", "engineer", "lawyer", "teacher", "doctor", "housekeeper",
        "receptionist", "janitor", "carpenter", "electrician", "accountant",
        "supervisor", "secretary", "auditor", "writer", "designer", "broker",
        "pharmacist", "cashier", "analyst", "manager", "librarian", "counselor",
        "chef", "mechanic", "plumber", "developer", "programmer", "scientist",
        "researcher", "consultant", "administrator", "attendant", "guard",
        "baker", "clerk", "editor", "physician", "surgeon", "therapist",
        "assistant", "director", "coordinator", "technician", "inspector",
        "investigator", "detective", "officer", "dispatcher", "firefighter",
        "paramedic", "veterinarian", "dentist", "hygienist", "nutritionist",
        "coach", "instructor", "tutor", "painter", "driver",
    ],

    # Demographic lexicon: gendered pronouns + demographic NEs
    "demographic_lexicon": [
        "he", "she", "his", "her", "him", "they", "their", "them",
        "man", "woman", "men", "women", "male", "female", "boy", "girl",
        "gentleman", "lady", "sir", "madam",
        "african", "asian", "hispanic", "latino", "latina",
        "white", "black", "caucasian", "american", "european",
    ],

    # Paths (absolute)
    "data_dir": "/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-e1/data",
    "figures_dir": "/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-e1/figures",
    "results_path": "/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-e1/results.json",
    "validation_path": "/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-e1/04_validation.md",
    "fasttext_model_path": "/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-e1/data/models/openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin",

    # Visualization settings
    "figure_size": (10, 6),
    "figure_size_heatmap": (12, 8),
    "dpi": 150,
    "color_scheme": "colorblind",
    "bar_color": "#4C72B0",
    "highlight_color": "#DD8452",
    "output_format": "png",
}
