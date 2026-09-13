"""LLM loading and internal signal extraction for HalluConform."""

import logging
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import MODEL_NAME, DEVICE, MAX_NEW_TOKENS

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None


def get_model_and_tokenizer():
    """Load model and tokenizer (cached)."""
    global _model, _tokenizer
    if _model is None:
        logger.info(f"Loading model {MODEL_NAME} on {DEVICE}...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        _tokenizer.pad_token = _tokenizer.eos_token
        _tokenizer.padding_side = "left"

        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            device_map=DEVICE,
            output_attentions=True,
            output_hidden_states=True,
            trust_remote_code=True,
            attn_implementation="eager",
        )
        _model.eval()
        logger.info("Model loaded.")
    return _model, _tokenizer


def generate_with_signals(question: str, model=None, tokenizer=None):
    """
    Generate a response to the question and extract internal signals.
    Returns:
        generation: str
        signals: dict with token_entropy, attention_consistency, hidden_divergence
    """
    if model is None or tokenizer is None:
        model, tokenizer = get_model_and_tokenizer()

    prompt = f"Answer the following question briefly:\n{question}\nAnswer:"
    inputs = tokenizer(
        prompt, return_tensors="pt", truncation=True, max_length=512
    ).to(DEVICE)

    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,  # greedy decoding for determinism
            return_dict_in_generate=True,
            output_scores=True,
            output_attentions=True,
            output_hidden_states=True,
        )

    # Decode the generated tokens (excluding input)
    generated_ids = outputs.sequences[0, input_len:]
    generation = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

    # Extract signals from generation steps
    scores = outputs.scores  # list of (vocab_size,) tensors per step
    attentions = outputs.attentions  # list per step, each is tuple of (batch, heads, seq, seq)
    hidden_states = outputs.hidden_states  # list per step, each is tuple of layers (batch, seq, hidden)

    n_steps = len(scores)
    if n_steps == 0:
        return generation, {
            "token_entropy": 0.0,
            "attention_consistency": 0.0,
            "hidden_divergence": 0.0,
        }

    # Signal 1: Token-level entropy
    entropies = []
    for step_scores in scores:
        # step_scores: (batch=1, vocab_size)
        logits = step_scores[0]  # (vocab_size,)
        probs = F.softmax(logits.float(), dim=-1)
        entropy = -(probs * torch.log(probs + 1e-10)).sum().item()
        entropies.append(entropy)
    token_entropy = float(np.mean(entropies))

    # Signal 2: Attention consistency (cross-layer variance of attention weights)
    attn_variances = []
    for step_attns in attentions:
        # step_attns: tuple of (batch, heads, seq, seq) for each layer
        # We look at the last token's attention to all previous tokens
        layer_attns = []
        for layer_attn in step_attns:
            # layer_attn: (1, heads, seq, seq)
            # Take mean over heads, look at last token's attention
            mean_attn = layer_attn[0].mean(dim=0)[-1, :]  # (seq,)
            layer_attns.append(mean_attn.float().cpu().numpy())
        if len(layer_attns) > 1:
            layer_attns = np.stack(layer_attns)  # (n_layers, seq)
            var = float(np.var(layer_attns, axis=0).mean())
            attn_variances.append(var)
    attention_consistency = float(np.mean(attn_variances)) if attn_variances else 0.0

    # Signal 3: Hidden-state trajectory divergence (cosine divergence between consecutive layers)
    hid_divergences = []
    for step_hiddens in hidden_states:
        # step_hiddens: tuple of (batch, seq, hidden) for each layer
        # Focus on the last token position
        layer_vecs = []
        for layer_h in step_hiddens:
            vec = layer_h[0, -1, :].float()  # last position
            layer_vecs.append(vec)
        for i in range(len(layer_vecs) - 1):
            cos_sim = F.cosine_similarity(
                layer_vecs[i].unsqueeze(0),
                layer_vecs[i + 1].unsqueeze(0),
            ).item()
            divergence = 1.0 - cos_sim
            hid_divergences.append(divergence)
    hidden_divergence = float(np.mean(hid_divergences)) if hid_divergences else 0.0

    signals = {
        "token_entropy": token_entropy,
        "attention_consistency": attention_consistency,
        "hidden_divergence": hidden_divergence,
    }

    return generation, signals


def check_answer_correctness(generation: str, gold_answers: list) -> int:
    """Check if generation contains any gold answer (case-insensitive)."""
    gen_lower = generation.lower().strip()
    for ans in gold_answers:
        if ans.lower().strip() in gen_lower:
            return 1
    return 0


def collect_signals_for_dataset(samples, model=None, tokenizer=None, log_every=20):
    """Collect signals and correctness labels for a list of samples."""
    if model is None or tokenizer is None:
        model, tokenizer = get_model_and_tokenizer()

    results = []
    for i, sample in enumerate(samples):
        if i % log_every == 0:
            logger.info(f"  Processing sample {i}/{len(samples)}...")
        try:
            generation, signals = generate_with_signals(
                sample["question"], model, tokenizer
            )
            correct = check_answer_correctness(generation, sample["answers"])
            results.append({
                "question": sample["question"],
                "generation": generation,
                "correct": correct,
                "domain": sample["domain"],
                "risk_level": sample["risk_level"],
                **signals,
            })
        except Exception as e:
            logger.warning(f"Error at sample {i}: {e}")
            results.append({
                "question": sample["question"],
                "generation": "",
                "correct": 0,
                "domain": sample.get("domain", "unknown"),
                "risk_level": sample.get("risk_level", "low"),
                "token_entropy": 0.0,
                "attention_consistency": 0.0,
                "hidden_divergence": 0.0,
            })

    return results
