"""Model module: GPT-2 from scratch."""
import torch
from transformers import GPT2Config, GPT2LMHeadModel
from config import TrainConfig, ScaledExperimentConfig

def build_gpt2_model(cfg) -> GPT2LMHeadModel:
    """Build GPT-2 model with random initialization."""
    config = GPT2Config(
        vocab_size=cfg.vocab_size,
        n_positions=cfg.seq_len,
        n_embd=cfg.n_embd,
        n_layer=cfg.n_layer,
        n_head=cfg.n_head,
        bos_token_id=50256,
        eos_token_id=50256,
    )
    model = GPT2LMHeadModel(config)
    print(f"Built GPT-2: {cfg.n_layer}L/{cfg.n_head}H/{cfg.n_embd}D, {sum(p.numel() for p in model.parameters())/1e6:.1f}M params")
    return model

def load_model_for_eval(checkpoint_path: str, cfg) -> GPT2LMHeadModel:
    """Load model from checkpoint for evaluation."""
    model = build_gpt2_model(cfg)
    state = torch.load(checkpoint_path, map_location="cpu")
    model.load_state_dict(state["model"])
    return model
