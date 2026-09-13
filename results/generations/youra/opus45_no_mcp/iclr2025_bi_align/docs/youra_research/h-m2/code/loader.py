"""H-M2 Loader: Load and validate H-M1 results."""
import json
from pathlib import Path

MODEL_FIELDS = [
    "confidence_Llama_2_7b_chat",
    "confidence_Llama_2_13b_cha",
    "confidence_Mistral_7B_Inst",
]

MODEL_KEY_MAP = {
    "meta-llama/Llama-2-7b-chat-hf": "confidence_Llama_2_7b_chat",
    "meta-llama/Llama-2-13b-chat-hf": "confidence_Llama_2_13b_cha",
    "mistralai/Mistral-7B-Instruct-v0.2": "confidence_Mistral_7B_Inst",
}


def load_results(path: str = None) -> list:
    """Load H-M1 results.json, returns per_task list."""
    if path is None:
        path = Path(__file__).parent.parent.parent / "h-m1" / "code" / "outputs" / "results.json"

    with open(path, "r") as f:
        data = json.load(f)

    per_task = data.get("per_task", [])
    if not per_task:
        raise ValueError("No per_task data in results.json")

    # Validate schema
    required = {"task_id", "task_type"} | set(MODEL_FIELDS)
    for i, task in enumerate(per_task[:5]):  # Check first 5
        missing = required - set(task.keys())
        if missing:
            raise ValueError(f"Task {i} missing fields: {missing}")

    return per_task


def load_full_results(path: str = None) -> dict:
    """Load full H-M1 results including aggregate."""
    if path is None:
        path = Path(__file__).parent.parent.parent / "h-m1" / "code" / "outputs" / "results.json"

    with open(path, "r") as f:
        return json.load(f)
