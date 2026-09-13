from datasets import load_dataset


def load_security_eval_prompts(dataset_id: str = "s2e-lab/SecurityEval") -> list[dict]:
    ds = load_dataset(dataset_id, split="train")
    prompts = []
    for i, item in enumerate(ds):
        prompt_text = item.get("prompt") or item.get("Prompt") or ""
        cwe = item.get("cwe") or item.get("CWE") or "unknown"
        lang = item.get("language") or item.get("Language") or "python"
        if lang.lower() == "python" or "python" in prompt_text.lower():
            prompts.append({
                "id": f"prompt_{i}",
                "prompt": prompt_text,
                "cwe": cwe
            })
    return prompts
