"""HH-RLHF prompt extraction for H-M2."""
import random
from datasets import load_dataset
import config as cfg


def extract_prompt(conversation: str) -> str:
    """Extract Human turn from HH-RLHF conversation."""
    parts = conversation.split('\n\nAssistant:')
    return parts[0].strip()


def load_hh_rlhf_prompts(n: int, seed: int) -> list:
    """Load Anthropic/hh-rlhf test split, extract unique Human-turn prompts, sample n."""
    ds = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base", split="test")

    prompts = set()
    for ex in ds:
        prompt = extract_prompt(ex["chosen"])
        if prompt:
            prompts.add(prompt)

    prompts = sorted(prompts)
    random.Random(seed).shuffle(prompts)
    return prompts[:n]


def format_mistral_prompt(prompt: str) -> str:
    """Wrap prompt with Mistral instruction format."""
    clean = prompt.replace("Human:", "").strip()
    return f"[INST] {clean} [/INST]"
