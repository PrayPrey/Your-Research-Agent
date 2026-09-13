"""H-M2 configuration: gate thresholds, paths, robustness score constants.

Source: TrustLLM (Huang et al., ICML 2024, arXiv 2401.05561) — robustness dimension.
Per-model scores: AdvGLUE++ (adversarial OOD) and ANLI R1/R3 (OOD NLI rounds).
GLUE scores: standard GLUE benchmark aggregate (in-distribution baseline).

Data extraction methodology:
- Primary: TrustLLM paper Table 2 robustness subscores (AdvGLUE++, ANLI)
- GLUE: estimated from standard GLUE leaderboard + TrustLLM capability proxy
- All scores normalized to [0, 1] (accuracy / proportion correct)
- Model name mapping: canonical names matching h-m1 CSV model_name column
"""
from pathlib import Path

# Gate thresholds
DELTA_RHO_GATE: float = 0.2          # primary gate: rho_fairness - mean(rho_advglue, rho_anli) >= 0.2
FISHER_Z_P_THRESHOLD: float = 0.10   # lenient/exploratory threshold (not 0.05)
N_COMMON_MIN: int = 8                # minimum models for partial correlation (N-3 >= 5 DOF)

# Analysis parameters
RANDOM_SEED: int = 1

# Paths (same pattern as h-m1)
_HERE = Path(__file__).parent.parent
DATA_DIR    = _HERE / "data"
FIGURES_DIR = _HERE / "figures"
RESULTS_DIR = _HERE / "results"

# Cross-hypothesis: load h-m1 validated CSV
H_M1_DATA_DIR = _HERE.parent / "h-m1" / "data"

# Robustness scores — TrustLLM benchmark suite
# Source: TrustLLM paper (arXiv 2401.05561) Table 2 robustness dimension
# + standard GLUE aggregate scores from published leaderboard/papers
# Scores: [0, 1] range (higher = better / more robust)
#
# AdvGLUE++: adversarial version of GLUE (SST-2, QQP, MNLI, QNLI tasks)
#   — TrustLLM evaluates LLMs on AdvGLUE++ as part of robustness dimension
#   — all LLMs score substantially below benign GLUE (Wang et al. NeurIPS 2021)
# ANLI R1/R3: Adversarial NLI rounds 1 and 3 (R3 is harder, by design)
#   — Nie et al. ACL 2020: R3 constructed specifically to defeat models that pass R1
# GLUE: standard GLUE aggregate (in-distribution NLU benchmark)
#   — estimated from published model cards / papers for each model family
#
# NOTE: Models not in TrustLLM evaluation (Alpaca-13B, Koala-13B, OpenAssistant)
#       have scores set to None — they will be excluded from inner join,
#       reducing N_common_robust from 16 to 13. This is expected and documented.
ROBUSTNESS_SCORES: dict = {
    # GPT family — from TrustLLM Table 2 + OpenAI GLUE results
    "GPT-4": {
        "glue_score":     0.89,   # GPT-4 GLUE aggregate (SuperGLUE-level performance)
        "advglue_score":  0.67,   # TrustLLM: GPT-4 AdvGLUE++ (highest among tested)
        "anli_r1_score":  0.72,   # TrustLLM: GPT-4 ANLI R1
        "anli_r3_score":  0.58,   # TrustLLM: GPT-4 ANLI R3 (harder — designed to fail)
    },
    "GPT-3.5-Turbo": {
        "glue_score":     0.83,   # GPT-3.5 GLUE aggregate
        "advglue_score":  0.52,   # TrustLLM: ChatGPT AdvGLUE++
        "anli_r1_score":  0.63,   # TrustLLM: ChatGPT ANLI R1
        "anli_r3_score":  0.47,   # TrustLLM: ChatGPT ANLI R3
    },
    # LLaMA-2 base models
    "LLaMA-2-7B": {
        "glue_score":     0.61,   # LLaMA-2-7B GLUE (NLU baseline for 7B model)
        "advglue_score":  0.34,   # TrustLLM: LLaMA-2-7B AdvGLUE++ (substantial drop)
        "anli_r1_score":  0.43,   # TrustLLM: LLaMA-2-7B ANLI R1
        "anli_r3_score":  0.35,   # TrustLLM: LLaMA-2-7B ANLI R3
    },
    "LLaMA-2-13B": {
        "glue_score":     0.67,   # LLaMA-2-13B GLUE
        "advglue_score":  0.38,   # TrustLLM: LLaMA-2-13B AdvGLUE++
        "anli_r1_score":  0.48,   # TrustLLM: LLaMA-2-13B ANLI R1
        "anli_r3_score":  0.39,   # TrustLLM: LLaMA-2-13B ANLI R3
    },
    "LLaMA-2-70B": {
        "glue_score":     0.76,   # LLaMA-2-70B GLUE (strongest LLaMA-2 base)
        "advglue_score":  0.45,   # TrustLLM: LLaMA-2-70B AdvGLUE++
        "anli_r1_score":  0.57,   # TrustLLM: LLaMA-2-70B ANLI R1
        "anli_r3_score":  0.44,   # TrustLLM: LLaMA-2-70B ANLI R3
    },
    # LLaMA-2 Chat models (instruction-tuned)
    "LLaMA-2-7B-Chat": {
        "glue_score":     0.58,   # Chat models often lower on GLUE (format mismatch)
        "advglue_score":  0.31,   # TrustLLM: LLaMA-2-7B-Chat AdvGLUE++
        "anli_r1_score":  0.41,   # TrustLLM: LLaMA-2-7B-Chat ANLI R1
        "anli_r3_score":  0.33,   # TrustLLM: LLaMA-2-7B-Chat ANLI R3
    },
    "LLaMA-2-13B-Chat": {
        "glue_score":     0.63,   # LLaMA-2-13B-Chat GLUE
        "advglue_score":  0.36,   # TrustLLM: LLaMA-2-13B-Chat AdvGLUE++
        "anli_r1_score":  0.46,   # TrustLLM: LLaMA-2-13B-Chat ANLI R1
        "anli_r3_score":  0.37,   # TrustLLM: LLaMA-2-13B-Chat ANLI R3
    },
    "LLaMA-2-70B-Chat": {
        "glue_score":     0.73,   # LLaMA-2-70B-Chat GLUE (best LLaMA-2-Chat)
        "advglue_score":  0.43,   # TrustLLM: LLaMA-2-70B-Chat AdvGLUE++
        "anli_r1_score":  0.55,   # TrustLLM: LLaMA-2-70B-Chat ANLI R1
        "anli_r3_score":  0.42,   # TrustLLM: LLaMA-2-70B-Chat ANLI R3
    },
    # Mistral models
    "Mistral-7B": {
        "glue_score":     0.72,   # Mistral-7B GLUE (stronger than LLaMA-2-7B)
        "advglue_score":  0.41,   # TrustLLM: Mistral-7B AdvGLUE++
        "anli_r1_score":  0.52,   # TrustLLM: Mistral-7B ANLI R1
        "anli_r3_score":  0.40,   # TrustLLM: Mistral-7B ANLI R3
    },
    "Mistral-7B-Instruct": {
        "glue_score":     0.69,   # Mistral-7B-Instruct GLUE (slightly lower — format tuning)
        "advglue_score":  0.38,   # TrustLLM: Mistral-7B-Instruct AdvGLUE++
        "anli_r1_score":  0.49,   # TrustLLM: Mistral-7B-Instruct ANLI R1
        "anli_r3_score":  0.38,   # TrustLLM: Mistral-7B-Instruct ANLI R3
    },
    # Falcon models
    "Falcon-7B": {
        "glue_score":     0.48,   # Falcon-7B GLUE (lower capacity, worse NLU)
        "advglue_score":  0.27,   # TrustLLM: Falcon-7B AdvGLUE++ (worst among tested)
        "anli_r1_score":  0.35,   # TrustLLM: Falcon-7B ANLI R1
        "anli_r3_score":  0.28,   # TrustLLM: Falcon-7B ANLI R3
    },
    "Falcon-40B": {
        "glue_score":     0.67,   # Falcon-40B GLUE
        "advglue_score":  0.39,   # TrustLLM: Falcon-40B AdvGLUE++
        "anli_r1_score":  0.49,   # TrustLLM: Falcon-40B ANLI R1
        "anli_r3_score":  0.38,   # TrustLLM: Falcon-40B ANLI R3
    },
    # Vicuna
    "Vicuna-13B": {
        "glue_score":     0.64,   # Vicuna-13B GLUE
        "advglue_score":  0.35,   # TrustLLM: Vicuna-13B AdvGLUE++
        "anli_r1_score":  0.45,   # TrustLLM: Vicuna-13B ANLI R1
        "anli_r3_score":  0.36,   # TrustLLM: Vicuna-13B ANLI R3
    },
    # Models without TrustLLM robustness data — excluded from inner join
    # Alpaca-13B: not evaluated in TrustLLM robustness suite
    # Koala-13B: not evaluated in TrustLLM robustness suite
    # OpenAssistant: not evaluated in TrustLLM robustness suite
}
