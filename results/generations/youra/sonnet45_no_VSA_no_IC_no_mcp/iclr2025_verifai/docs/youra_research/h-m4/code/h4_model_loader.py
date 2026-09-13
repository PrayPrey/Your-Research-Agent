"""Model and tokenizer loader for h-m4."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_model_and_tokenizer(model_name: str, device_str: str = "auto", dtype_str: str = "float16"):
    """
    Load model and tokenizer.

    Args:
        model_name: HuggingFace model ID
        device_str: "auto" | "cuda" | "cpu"
        dtype_str: "float16" | "float32"

    Returns:
        (model, tokenizer)
    """
    from pathlib import Path

    # Setup device
    if device_str == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_str)

    if device.type == "cuda":
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Using CPU (no GPU available)")

    # Find cached model
    cache_home = Path.home() / '.cache' / 'huggingface' / 'hub'
    model_dir = cache_home / 'models--codellama--CodeLlama-7b-hf'

    if model_dir.exists():
        snapshots = list((model_dir / 'snapshots').iterdir())
        if snapshots:
            local_path = str(snapshots[0])
            print(f"Using cached model at {local_path}")
            model_name = local_path

    # Load tokenizer
    print(f"Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)

    # Load model
    print(f"Loading model...")
    torch_dtype = torch.float16 if dtype_str == "float16" else torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch_dtype,
        device_map="auto" if device.type == "cuda" else None,
        low_cpu_mem_usage=True,
        local_files_only=True
    )

    if device.type == "cpu":
        model = model.to(device)

    print("Model loaded successfully.")
    return model, tokenizer
