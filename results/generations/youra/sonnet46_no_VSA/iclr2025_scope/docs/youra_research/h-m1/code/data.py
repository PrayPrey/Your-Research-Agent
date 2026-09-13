import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset
from config import Config

# Use h-e1 cache if it has the model
_HE1_CACHE = "/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scope/docs/youra_research/h-e1/checkpoints/mohawk/huggingface/hub"
if os.path.exists(_HE1_CACHE):
    os.environ.setdefault("HF_HUB_CACHE", _HE1_CACHE)
    os.environ.setdefault("TRANSFORMERS_CACHE", _HE1_CACHE)


def load_teacher(model_id: str = "meta-llama/Llama-3.1-8B"):
    """Returns (model, tokenizer). bfloat16, eager attention for dense matrices."""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=torch.bfloat16,
        device_map="cuda",
        attn_implementation="eager",
    )
    model.eval()
    return model, tokenizer


def sample_sequences(tokenizer, cfg: Config, seq_len: int) -> torch.Tensor:
    """Returns (n_samples, seq_len) token tensor; fixed seed."""
    dataset = load_dataset(
        cfg.dataset_id,
        cfg.dataset_subset,
        split=cfg.dataset_split,
        streaming=True,
    )
    gen = torch.Generator()
    gen.manual_seed(cfg.seed)

    sequences = []
    for item in dataset:
        if len(sequences) >= cfg.n_samples:
            break
        text = item["text"]
        enc = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=seq_len,
            padding="max_length",
        )
        if enc["input_ids"].shape[1] == seq_len:
            sequences.append(enc["input_ids"][0])

    if len(sequences) < cfg.n_samples:
        # pad by repeating if dataset too small
        while len(sequences) < cfg.n_samples:
            sequences.append(sequences[len(sequences) % len(sequences)])

    return torch.stack(sequences[:cfg.n_samples], dim=0)  # [n_samples, seq_len]


def _forward_with_attentions(model, input_ids: torch.Tensor) -> list:
    """Single forward pass; returns all_attentions list."""
    with torch.no_grad():
        outputs = model(
            input_ids=input_ids,
            output_attentions=True,
            use_cache=False,
        )
    return list(outputs.attentions)


def _select_head(
    attn_weights: torch.Tensor,
    layer_idx: int,
    sample_idx: int,
    base_seed: int = 42,
) -> torch.Tensor:
    """Select 1 random head. Seed is deterministic per (sample, layer)."""
    rng = torch.Generator()
    rng.manual_seed(base_seed + sample_idx * 32 + layer_idx)
    n_heads = attn_weights.shape[1]
    head_idx = torch.randint(0, n_heads, (1,), generator=rng).item()
    return attn_weights[0, head_idx]  # [N, N] bfloat16


def extract_attention_matrices(
    model,
    input_ids: torch.Tensor,  # [1, N]
    sample_idx: int,
    cfg: Config,
) -> torch.Tensor:  # [n_layers, N, N] bfloat16, on CPU
    """Extract 1 head per layer. Moves each layer result to CPU immediately."""
    all_attentions = _forward_with_attentions(model, input_ids)

    result = []
    for layer_idx, attn_weights in enumerate(all_attentions):
        head_attn = _select_head(attn_weights, layer_idx, sample_idx, cfg.seed)
        result.append(head_attn.cpu())
        del attn_weights
    del all_attentions
    torch.cuda.empty_cache()

    return torch.stack(result, dim=0)  # [n_layers, N, N] bfloat16 on CPU
