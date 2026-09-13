---
hypothesis_id: h-c1
phase: logic
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Logic: H-C1 — Cross-Benchmark Four-Way AUROC Ranking (TruthfulQA)

Applied: four-method-uncertainty-pipeline pattern (SE+SCG+TE+VC on same K=10 samples)
Applied: sequential-model-loading pattern (7B-hf → 7B-Chat; avoid dual OOM)
Applied: bootstrap-auroc-reuse-from-h-m2 (same pattern as h-m3, h-m4)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m4 and h-e2-v2 lineage)
**Status**: API signatures verified from h-m4 actual code (vc.py, evaluate.py)
**Analyzed Paths**:
- `docs/youra_research/h-m4/code/vc.py` — build_vc_prompt, extract_confidence, run_vc_inference verified
- `docs/youra_research/h-m4/code/evaluate.py` — load_bootstrap_auroc, compute_vc_auroc structure verified
**Relevant Symbols** (verified):
- `build_vc_prompt(question: str) -> str` — Llama-2-Chat [INST] template
- `extract_confidence(response: str) -> tuple[float, bool]` — 3-pattern regex cascade
- `load_bootstrap_auroc(hm2_code_dir: str)` — loads fn via sys.path injection
- `bootstrap_auroc(scores, labels, n_bootstrap, seed) -> (float, float, float)` — from h-m2

---

## External Dependencies API

```python
# From: h-m4/code/vc.py (ACTUAL CODE — reuse verbatim)
def build_vc_prompt(question: str) -> str:
    """Llama-2-Chat [INST]<<SYS>>...<</SYS>>\n\n{user_content} [/INST] format."""
    ...

def extract_confidence(response: str) -> tuple[float, bool]:
    """3-pattern regex cascade. Returns (confidence_0_1, parsed: bool). Fallback: (0.5, False)."""
    ...

# From: h-m2/code/evaluate.py (via h-m4 load pattern)
bootstrap_auroc(
    scores: list[float],   # uncertainty scores [N]
    labels: list[int],     # binary EM labels [N]
    n_bootstrap: int,      # 1000
    seed: int,             # 42
) -> tuple[float, float, float]  # (auroc_mean, ci_lo, ci_hi)
```

---

## A-3: Llama-2-7B Generation [Complexity: 14, Budget: 3 subtasks]

Applied: batched-generation with K-sample stochastic + greedy-logits-parallel

### L-3-1: load_base_model()

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def load_base_model(cfg: "Config") -> tuple:
    """
    Load Llama-2-7B-hf in float16 with device_map=auto.
    Returns (model, tokenizer).
    Tensor shape context: model weights in float16; input_ids [B, T].
    """
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id_base, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id_base,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model.eval()
    return model, tokenizer
```

### L-3-2: generate_k_samples()

```python
def generate_k_samples(
    questions: list[str],           # [N] question strings
    model,
    tokenizer,
    K: int = 10,                    # samples per question
    temperature: float = 0.7,
    max_new_tokens: int = 50,
    seed: int = 42,
    batch_size: int = 8,
) -> list[list[str]]:               # [N x K] decoded strings
    """
    Stochastic sampling for SE/SCG computation.
    For each question: K forward passes with temperature=0.7.

    Tensor shapes:
    - input_ids: [1, T_in] per question (batched across questions, not K)
    - output_ids: [1, T_in + max_new_tokens] per sample
    - K samples per question via loop (memory-safe vs batching K)

    Returns: list of K string samples per question.
    """
    torch.manual_seed(seed)
    all_samples = []

    for i in range(0, len(questions), batch_size):
        batch_questions = questions[i:i+batch_size]
        batch_samples = [[] for _ in batch_questions]

        prompts = [f"Q: {q}\nA:" for q in batch_questions]

        for k in range(K):
            inputs = tokenizer(prompts, return_tensors="pt", padding=True,
                               truncation=True, max_length=512).to(model.device)
            with torch.no_grad():
                output_ids = model.generate(
                    **inputs,
                    do_sample=True,
                    temperature=temperature,
                    max_new_tokens=max_new_tokens,
                    pad_token_id=tokenizer.eos_token_id,
                )
            # Decode only new tokens
            new_ids = output_ids[:, inputs["input_ids"].shape[1]:]
            decoded = tokenizer.batch_decode(new_ids, skip_special_tokens=True)
            for j, text in enumerate(decoded):
                batch_samples[j].append(text.strip())

        all_samples.extend(batch_samples)

    return all_samples  # [N x K]
```

### L-3-3: generate_greedy_with_logits()

```python
def generate_greedy_with_logits(
    questions: list[str],               # [N]
    model,
    tokenizer,
    max_new_tokens: int = 50,
    batch_size: int = 8,
) -> tuple[list[str], list[list[float]]]:  # (answers [N], log_probs [N x T_out])
    """
    Greedy decode with logit extraction for TE computation.
    Returns decoded answers and per-token log-probabilities.

    Tensor shapes:
    - logits: [B, T_out, vocab_size] → argmax → [B, T_out]
    - log_probs per token: log_softmax(logits[b, t]) → scalar
    - per_token_logprobs: [N x variable_T_out]
    """
    answers, all_logprobs = [], []

    for i in range(0, len(questions), batch_size):
        batch_q = questions[i:i+batch_size]
        prompts = [f"Q: {q}\nA:" for q in batch_q]
        inputs = tokenizer(prompts, return_tensors="pt", padding=True,
                           truncation=True, max_length=512).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=max_new_tokens,
                return_dict_in_generate=True,
                output_scores=True,
                pad_token_id=tokenizer.eos_token_id,
            )

        # outputs.scores: tuple of T_out tensors, each [B, vocab_size]
        import torch.nn.functional as F
        for b in range(len(batch_q)):
            new_ids = outputs.sequences[b, inputs["input_ids"].shape[1]:]
            answer = tokenizer.decode(new_ids, skip_special_tokens=True).strip()
            answers.append(answer)

            # Per-token log-probs for generated tokens
            token_logprobs = []
            for t, score in enumerate(outputs.scores):
                if t >= len(new_ids):
                    break
                log_probs = F.log_softmax(score[b], dim=-1)  # [vocab_size]
                token_id = new_ids[t].item()
                token_logprobs.append(log_probs[token_id].item())
            all_logprobs.append(token_logprobs)

    return answers, all_logprobs  # ([N], [N x T])
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | load_base_model | Llama-2-7B-hf float16, device_map=auto, pad_token fix |
| L-3-2 | generate_k_samples | K=10 stochastic samples per question; batched across N; seed-controlled |
| L-3-3 | generate_greedy_with_logits | Greedy decode + output_scores=True; per-token log_probs extraction |

---

## A-5: SE Computation [Complexity: 14, Budget: 3 subtasks]

Applied: DeBERTa-NLI-clustering-entropy pattern (Kuhn et al. 2023)

### L-5-1: load_nli_model()

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def load_nli_model(model_id: str = "cross-encoder/nli-deberta-v3-small"):
    """
    Load DeBERTa NLI cross-encoder for semantic clustering.
    Returns (nli_model, nli_tokenizer).
    Tensor: input_ids [1, T_concat], output logits [1, 3] (contradiction/neutral/entailment).
    """
    nli_tokenizer = AutoTokenizer.from_pretrained(model_id)
    nli_model = AutoModelForSequenceClassification.from_pretrained(model_id)
    nli_model.eval()
    return nli_model, nli_tokenizer
```

### L-5-2: nli_cluster()

```python
def nli_cluster(
    samples: list[str],   # K samples for one question
    nli_model,
    nli_tokenizer,
    device: str = "cpu",
) -> list[list[int]]:    # list of clusters (each cluster = list of sample indices)
    """
    Bidirectional entailment clustering.
    Two samples i,j in same cluster iff nli(i,j)=entailment AND nli(j,i)=entailment.
    Returns clusters (list of lists of indices).

    Tensor shape: inputs [1, T_i+T_j], logits [1, 3], entailment idx=2 per DeBERTa convention.
    """
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
                logits = nli_model(**enc).logits[0]  # [3]
            pred = logits.argmax().item()
            # DeBERTa v3 small label order: 0=contradiction, 1=neutral, 2=entailment
            entail_matrix[i][j] = (pred == 2)

    # Union-Find clustering
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
```

### L-5-3: compute_se()

```python
import math

def compute_se(
    all_samples: list[list[str]],  # [N x K]
    nli_model_id: str,
    batch_size: int = 1,
) -> list[float]:                  # [N] SE scores (higher = more uncertain)
    """
    For each question: cluster K samples → compute cluster entropy.
    se = -sum(p * log(p + eps)) where p = cluster_size / K.

    Returns SE uncertainty scores [N] (negated AUROC direction: higher se = less certain).
    """
    nli_model, nli_tokenizer = load_nli_model(nli_model_id)
    se_scores = []

    for samples in all_samples:  # samples: K strings
        K = len(samples)
        clusters = nli_cluster(samples, nli_model, nli_tokenizer)
        cluster_probs = [len(c) / K for c in clusters]
        se = -sum(p * math.log(p + 1e-10) for p in cluster_probs if p > 0)
        se_scores.append(se)

    return se_scores
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | load_nli_model | DeBERTa NLI cross-encoder loading; label convention documented |
| L-5-2 | nli_cluster | Bidirectional entailment + union-find clustering; [K x K] pairwise NLI calls |
| L-5-3 | compute_se | Cluster probability → Shannon entropy; [N] SE scores |

---

## A-8: AUROC Evaluation [Complexity: 12, Budget: 2 subtasks]

Applied: bootstrap-auroc-reuse-from-h-m2, four-method-gate-logic

### L-8-1: compute_all_aurocs()

```python
def compute_all_aurocs(
    se_scores: list[float],    # [N] — higher = more uncertain
    scg_scores: list[float],   # [N]
    te_scores: list[float],    # [N]
    vc_scores: list[float],    # [N]
    em_labels: list[int],      # [N] binary {0, 1}
    cfg: "Config",
) -> dict:
    """
    Bootstrap AUROC for all 4 methods. Returns comprehensive results dict.

    Note: sklearn roc_auc_score expects higher score = more uncertain (same label direction).
    Verify: higher uncertainty should correlate with lower EM (incorrect answers).
    If AUROC < 0.5 for a method, flip is a sign of inverted scoring.
    """
    bootstrap_auroc = load_bootstrap_auroc(cfg.hm2_code_dir)

    results = {}
    bootstrap_samples = {}  # For violin plot

    for method, scores in [("se", se_scores), ("scg", scg_scores),
                            ("te", te_scores), ("vc", vc_scores)]:
        auroc, ci_lo, ci_hi = bootstrap_auroc(scores, em_labels, cfg.n_bootstrap, cfg.seed)
        results[f"auroc_{method}"] = auroc
        results[f"auroc_{method}_ci"] = [ci_lo, ci_hi]

    # Gate evaluation
    gate_results = evaluate_gate(
        results["auroc_se"], results["auroc_scg"],
        results["auroc_te"], results["auroc_vc"]
    )
    results.update(gate_results)

    # Ranking string
    method_aurocs = {
        "SE": results["auroc_se"], "SCG": results["auroc_scg"],
        "TE": results["auroc_te"], "VC": results["auroc_vc"]
    }
    sorted_methods = sorted(method_aurocs.items(), key=lambda x: x[1], reverse=True)
    results["ranking"] = " > ".join(f"{m}({a:.4f})" for m, a in sorted_methods)

    return results
```

### L-8-2: evaluate_gate()

```python
def evaluate_gate(
    auroc_se: float,
    auroc_scg: float,
    auroc_te: float,
    auroc_vc: float,
) -> dict:
    """
    Three-tier gate evaluation for H-C1.
    Primary (gate condition): SE > TE — direction preserved cross-benchmark
    Secondary (informative): VC < TE — scale-degradation benchmark-agnostic
    Tertiary (informative): SE >= SCG > TE > VC — full ranking holds
    """
    gate_primary = auroc_se > auroc_te
    gate_secondary = auroc_vc < auroc_te
    gate_tertiary = (auroc_se >= auroc_scg) and (auroc_scg > auroc_te) and (auroc_te > auroc_vc)
    gate_passed = gate_primary  # SHOULD_WORK gate condition

    print(f"H-C1 TruthfulQA results: SE={auroc_se:.4f}, SCG={auroc_scg:.4f}, "
          f"TE={auroc_te:.4f}, VC={auroc_vc:.4f}")
    print(f"Ranking: SE>TE: {gate_primary} | VC<TE: {gate_secondary} | Full: {gate_tertiary}")
    print(f"Gate (primary SE>TE): {'PASS' if gate_primary else 'FAIL'}")

    return {
        "gate_primary": gate_primary,
        "gate_secondary": gate_secondary,
        "gate_tertiary": gate_tertiary,
        "gate_passed": gate_passed,
    }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | compute_all_aurocs | Bootstrap AUROC for 4 methods; ranking string; gate call |
| L-8-2 | evaluate_gate | Three-tier gate: primary SE>TE, secondary VC<TE, tertiary full ranking |

---

## A-9: Visualization [Complexity: 14, Budget: 3 subtasks]

Applied: grouped-bar-cross-benchmark, violin-bootstrap-distribution

### L-9-1: plot_auroc_comparison()

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_auroc_comparison(results: dict, cfg: "Config", out_path: str) -> None:
    """
    Bar chart: SE, SCG, TE, VC AUROC on TruthfulQA with 95% CI error bars.
    X-axis: methods. Y-axis: AUROC. Error bars: CI width / 2.
    Colors: cfg.color_se, cfg.color_scg, cfg.color_te, cfg.color_vc.
    """
    methods = ["SE", "SCG", "TE", "VC"]
    aurocs = [results[f"auroc_{m.lower()}"] for m in methods]
    cis = [results[f"auroc_{m.lower()}_ci"] for m in methods]
    colors = [cfg.color_se, cfg.color_scg, cfg.color_te, cfg.color_vc]
    yerrs = [[(a - ci[0]), (ci[1] - a)] for a, ci in zip(aurocs, cis)]
    yerrs_arr = np.array(yerrs).T  # [2, 4]

    fig, ax = plt.subplots(figsize=cfg.fig_size_bar, dpi=cfg.figure_dpi)
    x = np.arange(len(methods))
    bars = ax.bar(x, aurocs, color=colors, alpha=0.85, width=0.6,
                  yerr=yerrs_arr, capsize=5, error_kw={"elinewidth": 1.5})
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=12)
    ax.set_ylabel("AUROC", fontsize=12)
    ax.set_title("H-C1: Four-Method AUROC on TruthfulQA (N=200)", fontsize=13)
    ax.set_ylim(0, 1.0)
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.5, label="Random")
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.figure_dpi)
    plt.close()
```

### L-9-2: plot_cross_benchmark()

```python
def plot_cross_benchmark(
    results_hc1: dict,      # H-C1 TruthfulQA results
    hm4_baselines: dict,    # H-M4 TriviaQA baselines
    cfg: "Config",
    out_path: str,
) -> None:
    """
    Grouped bar: TriviaQA (H-M4) vs TruthfulQA (H-C1) for SE, TE, VC.
    SCG excluded from comparison (not in H-M4).
    X groups: [SE, TE, VC]. Each group: 2 bars (TriviaQA, TruthfulQA).
    """
    methods = ["SE", "TE", "VC"]
    hm4_vals = [
        hm4_baselines.get("auroc_se", 0.286),
        hm4_baselines.get("auroc_te", 0.4381),
        hm4_baselines.get("auroc_vc", 0.4463),
    ]
    hc1_vals = [results_hc1[f"auroc_{m.lower()}"] for m in methods]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=cfg.figure_dpi)
    x = np.arange(len(methods))
    width = 0.35
    ax.bar(x - width/2, hm4_vals, width, label="TriviaQA (H-M4, N=98)",
           color="#8172B2", alpha=0.75)
    ax.bar(x + width/2, hc1_vals, width, label="TruthfulQA (H-C1, N=200)",
           color="#C44E52", alpha=0.75)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=12)
    ax.set_ylabel("AUROC", fontsize=12)
    ax.set_title("Cross-Benchmark AUROC: TriviaQA vs TruthfulQA", fontsize=13)
    ax.set_ylim(0, 1.0)
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.5)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.figure_dpi)
    plt.close()
```

### L-9-3: plot_rank_ordering()

```python
def plot_rank_ordering(results: dict, cfg: "Config", out_path: str) -> None:
    """
    Point plot: method ranking sorted by AUROC descending.
    CI shown as horizontal error bars. Non-overlapping CI = statistically distinct.
    """
    methods_sorted = sorted(
        [("SE", results["auroc_se"], results["auroc_se_ci"]),
         ("SCG", results["auroc_scg"], results["auroc_scg_ci"]),
         ("TE", results["auroc_te"], results["auroc_te_ci"]),
         ("VC", results["auroc_vc"], results["auroc_vc_ci"])],
        key=lambda x: x[1], reverse=True
    )
    names = [m[0] for m in methods_sorted]
    vals = [m[1] for m in methods_sorted]
    cis = [m[2] for m in methods_sorted]
    xerrs = [[(v - ci[0]), (ci[1] - v)] for v, ci in zip(vals, cis)]
    xerrs_arr = np.array(xerrs).T

    fig, ax = plt.subplots(figsize=(7, 4), dpi=cfg.figure_dpi)
    y = np.arange(len(names))
    ax.errorbar(vals, y, xerr=xerrs_arr, fmt="o", capsize=5,
                color="#2d2d2d", elinewidth=1.5, markersize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=12)
    ax.set_xlabel("AUROC (95% CI)", fontsize=12)
    ax.set_title("H-C1 Method Ranking — TruthfulQA", fontsize=13)
    ax.axvline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.5)
    plt.tight_layout()
    plt.savefig(out_path, dpi=cfg.figure_dpi)
    plt.close()
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | plot_auroc_comparison | Bar chart: 4-method AUROC + CI error bars on TruthfulQA |
| L-9-2 | plot_cross_benchmark | Grouped bar: TriviaQA (H-M4) vs TruthfulQA (H-C1) for SE/TE/VC |
| L-9-3 | plot_rank_ordering | Horizontal point + CI plot; sorted descending by AUROC |
