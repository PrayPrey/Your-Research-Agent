"""Embedding extraction for H-M3 attractor analysis."""
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel


def load_tokenizer(cfg):
    """Load tokenizer with proper padding setup."""
    tokenizer = AutoTokenizer.from_pretrained(cfg.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    return tokenizer


def load_trained_model(cfg, checkpoint_path: str, device: str = "cuda"):
    """Load a trained model from checkpoint.

    Handles both full model and LoRA adapter checkpoints.
    """
    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        cfg.base_model,
        torch_dtype=torch.bfloat16 if cfg.bf16 else torch.float32,
        device_map=device,
    )

    # Try loading as LoRA adapter
    try:
        model = PeftModel.from_pretrained(model, checkpoint_path)
        model = model.merge_and_unload()
    except Exception:
        # Might be a full model checkpoint, try direct load
        try:
            model = AutoModelForCausalLM.from_pretrained(
                checkpoint_path,
                torch_dtype=torch.bfloat16 if cfg.bf16 else torch.float32,
                device_map=device,
            )
        except Exception as e:
            print(f"Warning: Could not load checkpoint {checkpoint_path}: {e}")
            # Return base model as fallback
            pass

    model.eval()
    return model


def extract_embeddings(
    model,
    tokenizer,
    prompts: list,
    device: str = "cuda",
    batch_size: int = 8,
    max_length: int = 512,
) -> np.ndarray:
    """Extract mean-pooled last-layer hidden states as embeddings.

    Args:
        model: Pretrained model
        tokenizer: Tokenizer
        prompts: List of text prompts
        device: Device to use
        batch_size: Batch size for processing
        max_length: Maximum sequence length

    Returns:
        [n_prompts, hidden_dim] array of embeddings
    """
    model.eval()
    all_embeds = []

    for i in range(0, len(prompts), batch_size):
        batch_prompts = prompts[i:i + batch_size]

        inputs = tokenizer(
            batch_prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        ).to(device)

        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)

        # Get last hidden layer
        last_hidden = outputs.hidden_states[-1]  # [B, L, hidden_dim]

        # Masked mean pooling
        mask = inputs["attention_mask"].unsqueeze(-1).float()  # [B, L, 1]
        pooled = (last_hidden * mask).sum(1) / mask.sum(1)  # [B, hidden_dim]

        all_embeds.append(pooled.cpu().float().numpy())

    return np.concatenate(all_embeds, axis=0)


def extract_all_model_embeddings(
    checkpoints: dict,
    cfg,
    probe_prompts: list,
    device: str = "cuda",
) -> dict:
    """Extract embeddings from all model checkpoints.

    Args:
        checkpoints: {model_id: checkpoint_path} mapping
        cfg: HM3Config
        probe_prompts: List of prompts to use as probes
        device: Device to use

    Returns:
        {model_id: [n_probes, hidden_dim]} mapping
    """
    tokenizer = load_tokenizer(cfg)
    result = {}

    for model_id, path in checkpoints.items():
        print(f"Extracting embeddings for {model_id}...")
        model = load_trained_model(cfg, path, device)
        embeddings = extract_embeddings(
            model, tokenizer, probe_prompts, device,
            batch_size=cfg.probe_batch_size,
            max_length=cfg.max_length,
        )
        result[model_id] = embeddings

        # Free memory
        del model
        torch.cuda.empty_cache()

    return result


def load_behavior_probes(cfg, n_probes: int = None) -> list:
    """Load behavior probe prompts from HH-RLHF dataset.

    Args:
        cfg: HM3Config
        n_probes: Number of probes to sample (default: cfg.n_probes)

    Returns:
        List of prompt strings
    """
    from datasets import load_dataset

    if n_probes is None:
        n_probes = cfg.n_probes

    dataset = load_dataset(cfg.dataset_name)
    probes = []

    # Sample from helpful-base and harmless-base
    for split in ["train"]:
        data = dataset[split]
        # Shuffle with fixed seed for reproducibility
        data = data.shuffle(seed=42)

        for i, example in enumerate(data):
            if len(probes) >= n_probes:
                break

            # Extract prompt from chosen response
            chosen = example.get("chosen", "")
            if "\n\nHuman:" in chosen and "\n\nAssistant:" in chosen:
                # Extract the human turn as the prompt
                parts = chosen.split("\n\nAssistant:")
                if parts:
                    prompt = parts[0].strip()
                    if prompt and len(prompt) > 20:
                        probes.append(prompt)

    return probes[:n_probes]
