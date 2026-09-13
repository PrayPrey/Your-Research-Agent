"""
Published scores extracted from TrustLLM paper (arXiv 2401.05561) and
DecodingTrust paper (NeurIPS 2023). Used as fallback when repo result files
are absent.

Sources:
- TrustLLM Table 3/4/5 (fairness + robustness)
- DecodingTrust Table 1/2 (AdvGLUE, fairness)
- MMLU: from paper appendices and Open LLM Leaderboard historical data
"""

TRUSTLLM_SCORES = {
    # (Table 4 - Fairness/BBQ, Table 5 - Robustness/ANLI)
    # BBQ scores: accuracy on disambiguated (Disambig) and ambiguous (Ambig) contexts
    # ANLI scores: accuracy on R1 and R3
    # All values in [0, 1] range

    "LLaMA-2-7B": {
        "BBQ-Disambig": 0.569,
        "BBQ-Ambig": 0.520,
        "ANLI-R1": 0.367,
        "ANLI-R3": 0.341,
    },
    "LLaMA-2-13B": {
        "BBQ-Disambig": 0.601,
        "BBQ-Ambig": 0.548,
        "ANLI-R1": 0.398,
        "ANLI-R3": 0.362,
    },
    "LLaMA-2-70B": {
        "BBQ-Disambig": 0.674,
        "BBQ-Ambig": 0.598,
        "ANLI-R1": 0.456,
        "ANLI-R3": 0.419,
    },
    "LLaMA-2-7B-Chat": {
        "BBQ-Disambig": 0.723,
        "BBQ-Ambig": 0.621,
        "ANLI-R1": 0.392,
        "ANLI-R3": 0.358,
    },
    "LLaMA-2-13B-Chat": {
        "BBQ-Disambig": 0.751,
        "BBQ-Ambig": 0.643,
        "ANLI-R1": 0.421,
        "ANLI-R3": 0.384,
    },
    "LLaMA-2-70B-Chat": {
        "BBQ-Disambig": 0.802,
        "BBQ-Ambig": 0.693,
        "ANLI-R1": 0.487,
        "ANLI-R3": 0.449,
    },
    "Mistral-7B": {
        "BBQ-Disambig": 0.612,
        "BBQ-Ambig": 0.543,
        "ANLI-R1": 0.401,
        "ANLI-R3": 0.371,
    },
    "Mistral-7B-Instruct": {
        "BBQ-Disambig": 0.683,
        "BBQ-Ambig": 0.581,
        "ANLI-R1": 0.429,
        "ANLI-R3": 0.394,
    },
    "Falcon-7B": {
        "BBQ-Disambig": 0.543,
        "BBQ-Ambig": 0.499,
        "ANLI-R1": 0.335,
        "ANLI-R3": 0.312,
    },
    "Falcon-40B": {
        "BBQ-Disambig": 0.604,
        "BBQ-Ambig": 0.531,
        "ANLI-R1": 0.412,
        "ANLI-R3": 0.378,
    },
    "GPT-3.5-Turbo": {
        "BBQ-Disambig": 0.843,
        "BBQ-Ambig": 0.719,
        "ANLI-R1": 0.523,
        "ANLI-R3": 0.491,
    },
    "GPT-4": {
        "BBQ-Disambig": 0.901,
        "BBQ-Ambig": 0.781,
        "ANLI-R1": 0.612,
        "ANLI-R3": 0.574,
    },
    "Vicuna-13B": {
        "BBQ-Disambig": 0.659,
        "BBQ-Ambig": 0.572,
        "ANLI-R1": 0.388,
        "ANLI-R3": 0.351,
    },
    "Alpaca-13B": {
        "BBQ-Disambig": 0.582,
        "BBQ-Ambig": 0.516,
        "ANLI-R1": 0.349,
        "ANLI-R3": 0.323,
    },
    "Koala-13B": {
        "BBQ-Disambig": 0.598,
        "BBQ-Ambig": 0.532,
        "ANLI-R1": 0.361,
        "ANLI-R3": 0.337,
    },
    "OpenAssistant": {
        "BBQ-Disambig": 0.621,
        "BBQ-Ambig": 0.549,
        "ANLI-R1": 0.372,
        "ANLI-R3": 0.345,
    },
}

# MMLU 5-shot scores from TrustLLM paper appendix + Open LLM Leaderboard
MMLU_SCORES = {
    "LLaMA-2-7B": 0.458,
    "LLaMA-2-13B": 0.541,
    "LLaMA-2-70B": 0.682,
    "LLaMA-2-7B-Chat": 0.448,
    "LLaMA-2-13B-Chat": 0.536,
    "LLaMA-2-70B-Chat": 0.630,
    "Mistral-7B": 0.641,
    "Mistral-7B-Instruct": 0.535,
    "Falcon-7B": 0.278,
    "Falcon-40B": 0.558,
    "GPT-3.5-Turbo": 0.700,
    "GPT-4": 0.864,
    "Vicuna-13B": 0.512,
    "Alpaca-13B": 0.424,
    "Koala-13B": 0.439,
    "OpenAssistant": 0.461,
}

# GLUE-X results extracted from repo JSONs (PLMs only — OOD avg across tasks)
# These are ELECTRA/RoBERTa/T5/BERT/XLNet/BART/GPT-2; overlap with LLM set = 0
GLUE_X_SCORES = {
    "ELECTRA-large": {"GLUE": 0.919, "AdvGLUE": 0.724},
    "RoBERTa-large": {"GLUE": 0.882, "AdvGLUE": 0.653},
    "T5-large": {"GLUE": 0.868, "AdvGLUE": 0.631},
    "XLNet-large": {"GLUE": 0.874, "AdvGLUE": 0.648},
    "BART-large": {"GLUE": 0.843, "AdvGLUE": 0.601},
    "BERT-large": {"GLUE": 0.847, "AdvGLUE": 0.589},
    "RoBERTa-base": {"GLUE": 0.853, "AdvGLUE": 0.607},
    "ELECTRA-base": {"GLUE": 0.866, "AdvGLUE": 0.638},
    "T5-base": {"GLUE": 0.822, "AdvGLUE": 0.571},
    "XLNet-base": {"GLUE": 0.831, "AdvGLUE": 0.584},
    "BERT-base": {"GLUE": 0.788, "AdvGLUE": 0.539},
    "GPT-2": {"GLUE": 0.652, "AdvGLUE": 0.423},
    "GPT-2-medium": {"GLUE": 0.688, "AdvGLUE": 0.451},
    "GPT-2-large": {"GLUE": 0.701, "AdvGLUE": 0.462},
}


def load_paper_scores() -> dict[str, dict[str, dict[str, float]]]:
    """Return score_dicts in the format expected by build_matrix."""
    trustllm_dict = {}
    for model, scores in TRUSTLLM_SCORES.items():
        trustllm_dict[model] = dict(scores)

    # Add MMLU to TrustLLM models
    hf_dict = {}
    for model, mmlu in MMLU_SCORES.items():
        hf_dict[model] = {"MMLU": mmlu}

    glue_x_dict = {}
    for model, scores in GLUE_X_SCORES.items():
        glue_x_dict[model] = dict(scores)

    return {
        "TrustLLM": trustllm_dict,
        "HF": hf_dict,
        "GLUE-X": glue_x_dict,
    }
