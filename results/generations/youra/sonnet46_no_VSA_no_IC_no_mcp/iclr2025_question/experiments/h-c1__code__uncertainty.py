import math
import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForCausalLM


def compute_te(per_token_logprobs):
    """Mean per-token Shannon entropy from greedy logprobs. Returns [N] TE scores."""
    te_scores = []
    for logprobs in per_token_logprobs:
        if not logprobs:
            te_scores.append(0.0)
            continue
        # logprobs are log P(token) at each position; entropy = -sum(p*log(p))
        # but we only have the chosen token's logprob, not full distribution
        # Use negative mean logprob as token entropy proxy (standard TE)
        mean_neg_logprob = -sum(logprobs) / len(logprobs)
        te_scores.append(mean_neg_logprob)
    return te_scores


def load_nli_model(model_id="cross-encoder/nli-deberta-v3-small"):
    """Load DeBERTa NLI cross-encoder. Returns (model, tokenizer)."""
    nli_tokenizer = AutoTokenizer.from_pretrained(model_id)
    nli_model = AutoModelForSequenceClassification.from_pretrained(model_id)
    nli_model.eval()
    return nli_model, nli_tokenizer


def nli_cluster(samples, nli_model, nli_tokenizer, device="cpu"):
    """Bidirectional entailment clustering. Returns list of clusters (list of index lists)."""
    K = len(samples)
    entail_matrix = [[False] * K for _ in range(K)]

    for i in range(K):
        for j in range(K):
            if i == j:
                entail_matrix[i][j] = True
                continue
            enc = nli_tokenizer(
                samples[i], samples[j],
                return_tensors="pt", truncation=True, max_length=256
            ).to(device)
            with torch.no_grad():
                logits = nli_model(**enc).logits[0]
            pred = logits.argmax().item()
            # DeBERTa v3 small: 0=contradiction, 1=neutral, 2=entailment
            entail_matrix[i][j] = (pred == 2)

    parent = list(range(K))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    for i in range(K):
        for j in range(K):
            if entail_matrix[i][j] and entail_matrix[j][i]:
                union(i, j)

    cluster_map = {}
    for i in range(K):
        root = find(i)
        cluster_map.setdefault(root, []).append(i)
    return list(cluster_map.values())


def compute_se(all_samples, nli_model_id, batch_size=1):
    """DeBERTa NLI clustering + cluster entropy. Returns [N] SE scores."""
    nli_model, nli_tokenizer = load_nli_model(nli_model_id)
    se_scores = []

    for idx, samples in enumerate(all_samples):
        K = len(samples)
        clusters = nli_cluster(samples, nli_model, nli_tokenizer)
        cluster_probs = [len(c) / K for c in clusters]
        se = -sum(p * math.log(p + 1e-10) for p in cluster_probs if p > 0)
        se_scores.append(se)
        if (idx + 1) % 20 == 0:
            print(f"SE: {idx + 1}/{len(all_samples)} done")

    return se_scores


def compute_scg(all_samples):
    """BERTScore pairwise consistency. Returns [N] SCG scores = 1 - mean_pairwise_score."""
    from bert_score import score as bert_score_fn

    scg_scores = []
    for idx, samples in enumerate(all_samples):
        K = len(samples)
        if K < 2:
            scg_scores.append(0.0)
            continue

        # Compute all pairwise F1 scores
        refs = []
        cands = []
        for i in range(K):
            for j in range(K):
                if i != j:
                    cands.append(samples[i])
                    refs.append(samples[j])

        _, _, F1 = bert_score_fn(cands, refs, lang="en", verbose=False,
                                  rescale_with_baseline=True)
        mean_f1 = F1.mean().item()
        scg_scores.append(1.0 - mean_f1)

        if (idx + 1) % 20 == 0:
            print(f"SCG: {idx + 1}/{len(all_samples)} done")

    return scg_scores


def compute_vc(questions, cfg):
    """
    Loads Llama-2-7B-Chat, reuses h-m4 build_vc_prompt + extract_confidence.
    Returns (vc_uncertainty_scores [N], fallback_count, raw_confidences [N]).
    """
    hm4_abs = os.path.abspath(os.path.join(os.path.dirname(__file__), cfg.hm4_code_dir))
    if hm4_abs not in sys.path:
        sys.path.insert(0, hm4_abs)
    from vc import build_vc_prompt, extract_confidence

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id_chat, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    try:
        model = AutoModelForCausalLM.from_pretrained(
            cfg.model_id_chat,
            torch_dtype=torch.float16,
            device_map="auto",
        )
    except RuntimeError:
        print("OOM with float16, falling back to 8bit")
        model = AutoModelForCausalLM.from_pretrained(
            cfg.model_id_chat,
            load_in_8bit=True,
            device_map="auto",
        )
    model.eval()

    vc_uncertainties = []
    raw_confidences = []
    fallback_count = 0

    for i, question in enumerate(questions):
        prompt = build_vc_prompt(question)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=cfg.max_new_tokens_vc,
                do_sample=False,
                temperature=1.0,
            )
        new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        response = tokenizer.decode(new_tokens, skip_special_tokens=True)
        confidence, parsed = extract_confidence(response)
        vc_uncertainties.append(1.0 - confidence)
        raw_confidences.append(confidence)
        if not parsed:
            fallback_count += 1
        if (i + 1) % 20 == 0:
            print(f"VC: {i + 1}/{len(questions)} done, fallbacks so far: {fallback_count}")

    del model
    torch.cuda.empty_cache()

    return vc_uncertainties, fallback_count, raw_confidences
