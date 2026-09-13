"""H-E1 configuration: constants, canonical model map, source priority."""
from pathlib import Path

REQUIRED_COLS = ["BBQ-Disambig", "BBQ-Ambig", "GLUE", "AdvGLUE", "ANLI-R1", "ANLI-R3", "MMLU"]
SOURCE_PRIORITY = ["TrustLLM", "DecodingTrust", "GLUE-X", "OOD_NLP", "HF"]
BENCHMARK_PAIRS = [
    ("BBQ-Disambig", "BBQ-Ambig"),
    ("GLUE", "AdvGLUE"),
    ("ANLI-R1", "ANLI-R3"),
]
N_COMMON_GATE = 10

CANONICAL_MAP = {
    # LLaMA-2 base
    "llama-2-7b": "LLaMA-2-7B",
    "llama2-7b": "LLaMA-2-7B",
    "meta-llama/llama-2-7b-hf": "LLaMA-2-7B",
    "llama-2-13b": "LLaMA-2-13B",
    "llama2-13b": "LLaMA-2-13B",
    "meta-llama/llama-2-13b-hf": "LLaMA-2-13B",
    "llama-2-70b": "LLaMA-2-70B",
    "meta-llama/llama-2-70b-hf": "LLaMA-2-70B",
    # LLaMA-2 chat
    "llama-2-7b-chat": "LLaMA-2-7B-Chat",
    "llama2-7b-chat-hf": "LLaMA-2-7B-Chat",
    "meta-llama/llama-2-7b-chat-hf": "LLaMA-2-7B-Chat",
    "llama-2-13b-chat": "LLaMA-2-13B-Chat",
    "meta-llama/llama-2-13b-chat-hf": "LLaMA-2-13B-Chat",
    "llama-2-70b-chat": "LLaMA-2-70B-Chat",
    "meta-llama/llama-2-70b-chat-hf": "LLaMA-2-70B-Chat",
    # Mistral
    "mistral-7b": "Mistral-7B",
    "mistral-7b-v0.1": "Mistral-7B",
    "mistralai/mistral-7b-v0.1": "Mistral-7B",
    "mistral-7b-instruct": "Mistral-7B-Instruct",
    "mistral-7b-instruct-v0.1": "Mistral-7B-Instruct",
    "mistralai/mistral-7b-instruct-v0.1": "Mistral-7B-Instruct",
    # Falcon
    "falcon-7b": "Falcon-7B",
    "tiiuae/falcon-7b": "Falcon-7B",
    "falcon-40b": "Falcon-40B",
    "tiiuae/falcon-40b": "Falcon-40B",
    # GPT
    "gpt-3.5-turbo": "GPT-3.5-Turbo",
    "gpt-3.5-turbo-0301": "GPT-3.5-Turbo",
    "gpt-4": "GPT-4",
    "gpt-4-0314": "GPT-4",
    # Vicuna / Alpaca
    "vicuna-13b": "Vicuna-13B",
    "vicuna-13b-v1.1": "Vicuna-13B",
    "lmsys/vicuna-13b-v1.1": "Vicuna-13B",
    "alpaca-13b": "Alpaca-13B",
    # GLUE-X PLMs
    "electra-large": "ELECTRA-large",
    "roberta-large": "RoBERTa-large",
    "t5-large": "T5-large",
    "t5-base": "T5-base",
    "bart-large": "BART-large",
    "xlnet-large": "XLNet-large",
    "bert-large": "BERT-large",
    "bert-base": "BERT-base",
    "distilbert": "DistilBERT",
    "albert": "ALBERT",
    "gpt2": "GPT-2",
    "gpt2-medium": "GPT-2-medium",
    "gpt2-large": "GPT-2-large",
    "gpt2-xl": "GPT-2-XL",
}

# Paths relative to h-e1 root
_HERE = Path(__file__).parent.parent
FIGURES_DIR = _HERE / "figures"
RESULTS_DIR = _HERE / "results"
