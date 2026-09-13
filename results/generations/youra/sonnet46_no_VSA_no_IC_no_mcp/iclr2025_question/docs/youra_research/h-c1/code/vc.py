import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

SYSTEM_PROMPT = (
    "You are a helpful and honest assistant. "
    "When answering, provide your answer and then state your confidence "
    "as a percentage (0-100%)."
)


def load_vc_model(cfg) -> tuple:
    """Returns (model, tokenizer) for Llama-2-7B-Chat in float16."""
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model.eval()
    return model, tokenizer


def build_vc_prompt(question: str) -> str:
    """Build Llama-2-Chat [INST]...[/INST] prompt requesting Answer + Confidence."""
    user_content = (
        f"Question: {question}\n\n"
        "Please provide:\n"
        "1. Your answer\n"
        "2. Your confidence in your answer as a percentage (0-100%)\n\n"
        "Format: Answer: <your answer>\nConfidence: <number>%"
    )
    return (
        f"[INST] <<SYS>>\n{SYSTEM_PROMPT}\n<</SYS>>\n\n"
        f"{user_content} [/INST]"
    )


def extract_confidence(response: str) -> tuple:
    """
    3-pattern regex cascade. Returns (confidence_0_1, parsed: bool).
    Fallback: (0.5, False).
    """
    # Pattern 1: "Confidence: 85%" or "Confidence: 85.5%"
    m = re.search(r"[Cc]onfidence[:\s]+(\d+(?:\.\d+)?)\s*%", response)
    if m:
        val = float(m.group(1))
        return min(max(val / 100.0, 0.0), 1.0), True

    # Pattern 2: standalone "85%" anywhere in response
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*%", response)
    if m:
        val = float(m.group(1))
        return min(max(val / 100.0, 0.0), 1.0), True

    # Pattern 3: "I am 85 percent confident"
    m = re.search(r"\b(\d+(?:\.\d+)?)\s+percent", response, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        return min(max(val / 100.0, 0.0), 1.0), True

    return 0.5, False


def compute_vc_uncertainty(question: str, model, tokenizer, device: str) -> tuple:
    """Single greedy forward pass. Returns (uncertainty=1-confidence, parsed)."""
    prompt = build_vc_prompt(question)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=80,
            do_sample=False,
            temperature=1.0,
        )
    # Decode only newly generated tokens
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(new_tokens, skip_special_tokens=True)
    confidence, parsed = extract_confidence(response)
    return 1.0 - confidence, parsed


def run_vc_inference(questions: list, model, tokenizer, device: str) -> tuple:
    """
    Iterates all questions. Returns (vc_uncertainties, fallback_count).
    """
    vc_uncertainties = []
    fallback_count = 0

    for i, question in enumerate(questions):
        uncertainty, parsed = compute_vc_uncertainty(question, model, tokenizer, device)
        vc_uncertainties.append(uncertainty)
        if not parsed:
            fallback_count += 1
        confidence_val = round(1.0 - uncertainty, 4)
        print(f"[{i+1}/{len(questions)}] Parsed confidence: {confidence_val:.2f} (parsed={parsed})")

    return vc_uncertainties, fallback_count


def verify_vc_mechanism(
    vc_uncertainties: list,
    fallback_count: int,
    n_questions: int,
    auroc_vc: float,
    cfg,
) -> tuple:
    """
    Checks: parse_rate_ok (>=0.80), not_all_same (distinct scores>5),
    auroc_computed. Returns (activated, indicators).
    """
    parse_rate = 1.0 - (fallback_count / n_questions)
    parse_rate_ok = parse_rate >= cfg.parse_rate_gate

    distinct_scores = len(set(round(u, 3) for u in vc_uncertainties))
    not_all_same = distinct_scores > 5

    auroc_computed = auroc_vc is not None and not (auroc_vc != auroc_vc)  # not NaN

    activated = parse_rate_ok and not_all_same and auroc_computed

    indicators = {
        "parse_rate": round(parse_rate, 4),
        "parse_rate_ok": parse_rate_ok,
        "distinct_scores": distinct_scores,
        "not_all_same": not_all_same,
        "auroc_computed": auroc_computed,
        "fallback_count": fallback_count,
    }

    print(f"Mechanism verification: parse_rate={parse_rate:.3f}, distinct={distinct_scores}, activated={activated}")
    return activated, indicators
