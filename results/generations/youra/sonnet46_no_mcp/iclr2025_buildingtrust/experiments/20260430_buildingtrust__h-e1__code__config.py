from __future__ import annotations

MODELS: list[dict] = [
    # Pythia family (replaces gated Llama-2/3 — publicly accessible)
    {"id": "pythia-6.9b",  "hf_id": "EleutherAI/pythia-6.9b-deduped",  "params": "7B",  "family": "pythia", "requires_4bit": False},
    {"id": "pythia-12b",   "hf_id": "EleutherAI/pythia-12b-deduped",   "params": "13B", "family": "pythia", "requires_4bit": False},
    # Mistral family
    {"id": "mistral-7b-instruct-v01",  "hf_id": "mistralai/Mistral-7B-Instruct-v0.1",   "params": "7B",  "family": "mistral", "requires_4bit": False},
    {"id": "mistral-7b-instruct-v02",  "hf_id": "mistralai/Mistral-7B-Instruct-v0.2",   "params": "7B",  "family": "mistral", "requires_4bit": False},
    {"id": "mistral-7b-instruct-v03",  "hf_id": "mistralai/Mistral-7B-Instruct-v0.3",   "params": "7B",  "family": "mistral", "requires_4bit": False},
    {"id": "mixtral-8x7b-instruct",    "hf_id": "mistralai/Mixtral-8x7B-Instruct-v0.1", "params": "40B", "family": "mistral", "requires_4bit": False},
    # Falcon family
    {"id": "falcon-7b-instruct",  "hf_id": "tiiuae/falcon-7b-instruct",  "params": "7B",  "family": "falcon", "requires_4bit": False},
    {"id": "falcon-40b-instruct", "hf_id": "tiiuae/falcon-40b-instruct", "params": "40B", "family": "falcon", "requires_4bit": False},
    # Vicuna family
    {"id": "vicuna-7b-v15",  "hf_id": "lmsys/vicuna-7b-v1.5",  "params": "7B",  "family": "vicuna", "requires_4bit": False},
    {"id": "vicuna-13b-v15", "hf_id": "lmsys/vicuna-13b-v1.5", "params": "13B", "family": "vicuna", "requires_4bit": False},
    # Zephyr family
    {"id": "zephyr-7b-beta",  "hf_id": "HuggingFaceH4/zephyr-7b-beta",  "params": "7B", "family": "zephyr", "requires_4bit": False},
    {"id": "zephyr-7b-alpha", "hf_id": "HuggingFaceH4/zephyr-7b-alpha", "params": "7B", "family": "zephyr", "requires_4bit": False},
    # OpenHermes / Nous family
    {"id": "openhermes-25-mistral-7b", "hf_id": "teknium/OpenHermes-2.5-Mistral-7B",           "params": "7B", "family": "nous", "requires_4bit": False},
    {"id": "nous-hermes2-mistral-7b",  "hf_id": "NousResearch/Nous-Hermes-2-Mistral-7B-DPO",   "params": "7B", "family": "nous", "requires_4bit": False},
    # WizardLM family
    {"id": "wizardlm-13b-v12", "hf_id": "WizardLM/WizardLM-13B-V1.2", "params": "13B", "family": "wizardlm", "requires_4bit": False},
    {"id": "wizardlm-70b-v10", "hf_id": "WizardLM/WizardLM-70B-V1.0", "params": "70B", "family": "wizardlm", "requires_4bit": True},
    # Qwen family
    {"id": "qwen15-7b-chat",  "hf_id": "Qwen/Qwen1.5-7B-Chat",  "params": "7B",  "family": "qwen", "requires_4bit": False},
    {"id": "qwen15-14b-chat", "hf_id": "Qwen/Qwen1.5-14B-Chat", "params": "13B", "family": "qwen", "requires_4bit": False},
    {"id": "qwen15-72b-chat", "hf_id": "Qwen/Qwen1.5-72B-Chat", "params": "70B", "family": "qwen", "requires_4bit": True},
    # Yi family
    {"id": "yi-6b-chat",  "hf_id": "01-ai/Yi-6B-Chat",  "params": "7B",  "family": "yi", "requires_4bit": False},
    {"id": "yi-34b-chat", "hf_id": "01-ai/Yi-34B-Chat",  "params": "30B", "family": "yi", "requires_4bit": False},
    # DeepSeek family
    {"id": "deepseek-7b-chat",  "hf_id": "deepseek-ai/deepseek-llm-7b-chat",  "params": "7B",  "family": "deepseek", "requires_4bit": False},
    {"id": "deepseek-67b-chat", "hf_id": "deepseek-ai/deepseek-llm-67b-chat", "params": "70B", "family": "deepseek", "requires_4bit": True},
    # InternLM family
    {"id": "internlm2-7b-chat",  "hf_id": "internlm/internlm2-chat-7b",  "params": "7B",  "family": "internlm", "requires_4bit": False},
    {"id": "internlm2-20b-chat", "hf_id": "internlm/internlm2-chat-20b", "params": "30B", "family": "internlm", "requires_4bit": False},
    # Phi family
    {"id": "phi2", "hf_id": "microsoft/phi-2", "params": "7B", "family": "phi", "requires_4bit": False},
    # Solar family
    {"id": "solar-10-7b-instruct", "hf_id": "upstage/SOLAR-10.7B-Instruct-v1.0", "params": "13B", "family": "solar", "requires_4bit": False},
    # Orca family (replaces gated MPT models)
    {"id": "orca-2-13b", "hf_id": "microsoft/Orca-2-13b", "params": "13B", "family": "orca", "requires_4bit": False},
    # Starling family
    {"id": "starling-7b-alpha", "hf_id": "berkeley-nest/Starling-LM-7B-alpha", "params": "7B", "family": "starling", "requires_4bit": False},
]

TASKS: list[str] = ["mmlu", "truthfulqa_mc1", "anli_r3", "humaneval"]

RESULTS_DIR: str = "h-e1/results/"
FIGURES_DIR: str = "h-e1/figures/"

GREEDY_SEED: int = 42
STOCHASTIC_SEEDS: list[int] = [42, 123, 456]
STOCHASTIC_TEMPERATURE: float = 0.7

ECE_BINS: int = 10
N_BOOTSTRAP: int = 10000

BATCH_SIZE: dict = {"7B": 8, "13B": 8, "30B": 4, "40B": 4, "70B": 1}

INDICATORS: list[str] = ["ECE", "Brier", "TruthfulQA_pct", "ANLI_drop"]
COVARIATE: str = "MMLU_acc"
GATE_PAIRS: list[tuple] = [("ECE", "TruthfulQA_pct"), ("ECE", "ANLI_drop")]
GATE_THRESHOLD: float = 0.40
MIN_MODELS: int = 25

N_FACTORS: int = 1
FA_METHOD: str = "ml"
FA_ROTATION: str = "promax"
TUCKER_CONGRUENCE_THRESHOLD: float = 0.85

FIGURE_DPI: int = 150
FIGURE_FORMAT: str = "png"
FIGURE_NAMES: dict = {
    "partial_corr_heatmap":   "fig1_partial_corr_heatmap.png",
    "factor_loadings":        "fig2_factor_loadings.png",
    "ece_truthfulqa_scatter": "fig3_ece_truthfulqa_scatter.png",
    "ece_advglue_scatter":    "fig4_ece_advglue_scatter.png",
    "ece_anli_scatter":       "fig5_ece_anli_scatter.png",
    "loo_roc_curve":          "fig6_loo_roc_curve.png",
}
