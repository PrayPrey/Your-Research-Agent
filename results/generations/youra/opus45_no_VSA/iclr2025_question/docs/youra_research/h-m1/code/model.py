# model.py - NTI extraction via TransformerLens
import torch
import numpy as np
from transformer_lens import HookedTransformer
from config import CONFIG


def load_model(model_id=None, device=None):
    """Load LLaMA-2-7B via TransformerLens with fp16."""
    model_id = model_id or CONFIG["model_id"]
    device = device or CONFIG["device"]
    model = HookedTransformer.from_pretrained(
        model_id,
        device=device,
        dtype=torch.float16,
    )
    model.eval()
    return model


def compute_nti(model, input_ids, target_layers=None):
    """
    Compute NTI = std(entropy)/mean(entropy) across target_layers.
    Returns (nti[B], trajectory[B, num_layers]).
    """
    target_layers = target_layers or CONFIG["target_layers"]
    layer_start, layer_end = target_layers
    num_layers = layer_end - layer_start + 1

    # Get activation cache for target layers only
    names_filter = lambda name: any(
        f"blocks.{l}.hook_resid_post" in name
        for l in range(layer_start, layer_end + 1)
    )

    with torch.no_grad():
        _, cache = model.run_with_cache(input_ids, names_filter=names_filter)

    # Compute entropy per layer via logit-lens (fp32 for numerical stability)
    entropies = []
    for l in range(layer_start, layer_end + 1):
        residual = cache[f"blocks.{l}.hook_resid_post"][:, -1, :]  # [B, d_model]
        # Logit-lens: ln_final -> W_U (convert to float32 for stable entropy)
        normed = model.ln_final(residual).float()
        logits = normed @ model.W_U.float()  # [B, vocab]
        probs = torch.softmax(logits, dim=-1)
        entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)  # [B]
        entropies.append(entropy)

    trajectory = torch.stack(entropies, dim=1)  # [B, num_layers]
    mean_ent = trajectory.mean(dim=1)
    std_ent = trajectory.std(dim=1)
    nti = std_ent / (mean_ent + 1e-8)  # [B]

    # Replace NaN/Inf with 0
    nti = torch.nan_to_num(nti, nan=0.0, posinf=0.0, neginf=0.0)
    trajectory = torch.nan_to_num(trajectory, nan=0.0, posinf=0.0, neginf=0.0)

    return nti, trajectory


def compute_baseline_entropy(model, input_ids):
    """Final-layer entropy baseline. Returns entropy[B]."""
    with torch.no_grad():
        logits = model(input_ids)[:, -1, :]  # [B, vocab]
    probs = torch.softmax(logits, dim=-1)
    entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
    return entropy


def extract_all_scores(model, prompts, batch_size=None):
    """
    Extract NTI, trajectory, and baseline_entropy for all prompts.
    Returns dict with numpy arrays.
    """
    batch_size = batch_size or CONFIG["batch_size"]
    device = CONFIG["device"]

    all_nti = []
    all_trajectory = []
    all_baseline = []

    for i in range(0, len(prompts), batch_size):
        batch_prompts = prompts[i:i+batch_size]
        tokens = model.to_tokens(batch_prompts, prepend_bos=True)
        tokens = tokens.to(device)

        nti, trajectory = compute_nti(model, tokens)
        baseline = compute_baseline_entropy(model, tokens)

        all_nti.append(nti.detach().cpu().numpy())
        all_trajectory.append(trajectory.detach().cpu().numpy())
        all_baseline.append(baseline.detach().cpu().numpy())

        # Clear cache periodically
        if i % (batch_size * 10) == 0:
            torch.cuda.empty_cache()

    return {
        "nti": np.concatenate(all_nti),
        "trajectory": np.concatenate(all_trajectory),
        "baseline_entropy": np.concatenate(all_baseline),
    }
