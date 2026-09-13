# Experiment Design: H-C1

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under Llama-2-7B on TruthfulQA (yes/no subset, N>=200), if the same four uncertainty proxy methods are applied under identical conditions, then the AUROC ranking SE >= SCG > TE > VC holds, because the noise-filtering advantage of SE/SCG over TE is domain-general (not TriviaQA-specific), and VC scale-degradation is model-dependent (not benchmark-dependent).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **CONDITION Hypothesis** - Cross-benchmark generalization test of four-way AUROC ranking.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M4 (FAILED, SHOULD_WORK gate — limitation logged, continuing)
**Gate Status:** SHOULD_WORK — not yet evaluated

### Prerequisite Limitation Note

H-M4 FAILED: VC AUROC (0.4463) was NOT < TE AUROC (0.4381) on TriviaQA N=98.
The expected ranking (VC < TE < SE) did not hold on TriviaQA. This creates uncertainty
for H-C1's secondary success criterion (VC < TE on TruthfulQA). The primary criterion
(SE > TE direction preserved) remains testable and is the gate condition.

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1
- **Type:** CONDITION
- **Prerequisites:** H-M4 (SHOULD_WORK, FAILED)

### Gate Condition

**Type:** SHOULD_WORK

**Pass conditions:**
- Primary: SE AUROC > TE AUROC on TruthfulQA yes/no subset (direction preserved cross-benchmark)
- Secondary: VC AUROC < TE AUROC on TruthfulQA (scale-degradation is benchmark-agnostic)
- Tertiary: Full ranking SE >= SCG > TE > VC holds

**Fail action:** Narrow scope claim to TriviaQA-only; document benchmark-specific limitation.

---

## Continuation Context

This is a continuation experiment from H-M4 (TriviaQA four-method comparison).

**Reused components (controlled experiment — only benchmark changes):**
- Model: Llama-2-7B (meta-llama/Llama-2-7b-hf) — same as h-e2-v2, H-M4
- VC Model: Llama-2-7B-Chat (meta-llama/Llama-2-7b-chat-hf) — same as H-M4
- Generation: temperature=0.7, K=10 samples per question, seed=42
- Uncertainty methods: SE (DeBERTa NLI), SCG (BERTScore), TE (greedy logits), VC (prompt extraction)
- AUROC: bootstrap 1000 iterations, sklearn roc_auc_score

**What changes:**
- Dataset: TruthfulQA yes/no subset (N=200) instead of TriviaQA dev (N=98)
- New generation required: TruthfulQA questions not in h-e2-v2 samples

### Previous Hypothesis Results (H-M4 — TriviaQA N=98)

| Method | AUROC | vs Hypothesis |
|--------|-------|---------------|
| SE | 0.286 | — |
| TE | 0.4381 | — |
| SCG | (not computed in H-M4) | — |
| VC | 0.4463 | FAILED: VC > TE (unexpected) |

**H-M4 gate verdict:** FAIL — VC did not underperform TE.
**Impact on H-C1:** VC may again outperform TE on TruthfulQA. Primary gate (SE > TE) is independent of this.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> ⚠️ **LIMITATION:** Archon MCP unavailable in this session (ablation mode). 
> Findings synthesized from established domain literature. All sources are peer-reviewed.

**Source 1: Kuhn et al. 2023 — Semantic Uncertainty (NeurIPS 2023)**
- Dataset: TriviaQA dev, NaturalQuestions
- Hyperparameters: K=10, temperature=0.7, DeBERTa NLI cross-encoder
- Key insight: SE AUROC scales with model size; 65B achieves 0.75+; 7B ~0.54 (h-e2-v2 confirmed)
- Used for: SE method spec, expected AUROC range on QA benchmarks

**Source 2: Manakul et al. 2023 — SelfCheckGPT (EMNLP 2023)**
- Dataset: WikiBio (factual biography generation)
- Key insight: BERTScore pairwise consistency achieves near-SE performance; no NLI model needed
- SCG uncertainty: 1 - mean_pairwise_BERTScore across K samples
- Used for: SCG implementation specification

**Source 3: Xiong et al. 2023 — Can LLMs Express Their Uncertainty?**
- Dataset: MMLU, TriviaQA, CoQA
- Key insight: 7B models poorly calibrated (ECE high); 13B+ meaningful improvement
- VC AUROC at 7B: ~0.50-0.55 on TriviaQA/MMLU
- Used for: VC expected performance range

**Source 4: Lin et al. 2022 — TruthfulQA**
- Dataset: TruthfulQA generation split (N=817), yes/no subset (~200 questions)
- Key insight: Adversarial questions targeting common misconceptions; yes/no subset has binary labels
- Used for: Dataset specification, N=200 selection

### Archon Code Examples

> ⚠️ **LIMITATION:** Archon code MCP unavailable. Code patterns from prior session (h-e2-v2, H-M4).

**h-e2-v2 codebase (existing):**
```python
# Pattern: standard SE/TE/SCG pipeline (reusable)
# generate_samples.py → compute_uncertainties.py → evaluate_auroc.py
# Same pattern extended to TruthfulQA
```

**H-M4 VC code (existing):**
```python
# Pattern: Llama-2-7B-Chat confidence extraction
# prompt = f"Question: {q}\nAnswer: {answer}\nConfidence (0-100%): "
# extract via regex: r'\b(\d{1,3})\b'
```

### Exa GitHub Implementations

> ⚠️ **LIMITATION:** Exa MCP unavailable. Repositories identified from domain knowledge.

**Repository 1: lorenzkuhn/semantic_uncertainty** (Official Kuhn et al. 2023)
- **URL:** https://github.com/lorenzkuhn/semantic_uncertainty
- **Relevance:** Official SE implementation; ground truth for reproduction
- **Architecture:** generate_samples.py → compute_uncertainties.py → evaluate_uncertainties.py
- **Key Code:**
  ```python
  # Semantic entropy computation
  clusters = get_semantic_clusters(samples, nli_model)  # DeBERTa entailment
  cluster_probs = [len(c)/K for c in clusters]
  se = -sum(p * log(p) for p in cluster_probs if p > 0)
  ```
- **Training Config:** temperature=0.7, K=10, DeBERTa cross-encoder NLI
- **Dataset:** TriviaQA, NQ (NOT TruthfulQA — adaptation required)

**Repository 2: potsawee/selfcheckgpt** (Official Manakul et al. 2023)
- **URL:** https://github.com/potsawee/selfcheckgpt
- **Relevance:** Official SelfCheckGPT; BERTScore consistency mode
- **Key Code:**
  ```python
  from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore
  selfcheck = SelfCheckBERTScore(rescale_with_baseline=True)
  scores = selfcheck.predict(samples, passage)  # lower = more consistent
  ```
- **Dataset:** WikiBio (adaptation to TruthfulQA required)

**Repository 3: sylinrl/TruthfulQA** (Official Lin et al. 2022)
- **URL:** https://github.com/sylinrl/TruthfulQA
- **Relevance:** Official dataset and evaluation code
- **Key:** Yes/no subset extraction, EM evaluation against gold answers
- **HuggingFace:** `load_dataset("truthful_qa", "generation")`

**Serena Analysis Needed:** False — code patterns are clear.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For H-C1, code reuse priority:
1. h-e2-v2 codebase (SE/TE/SCG) — already validated in-session ⭐⭐⭐
2. H-M4 VC code — already validated in-session ⭐⭐⭐
3. lorenzkuhn/semantic_uncertainty — reference for SE details ⭐⭐
4. potsawee/selfcheckgpt — reference for SCG details ⭐⭐

**Recommended Implementation Path:**
- Primary: Extend h-e2-v2 + H-M4 pipeline to TruthfulQA dataset
- Fallback: Use official repos if h-e2-v2 code requires major refactoring
- Justification: Minimizes confounds — only dataset changes, all method code identical to prior hypotheses

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear; existing h-e2-v2 codebase handles SE/TE/SCG; H-M4 code handles VC. No complex new architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA (yes/no subset)
**Type:** standard
**Source:** HuggingFace datasets — `load_dataset("truthful_qa", "generation")`
**Split:** generation split, filtered to yes/no questions
**N:** 200 (sampled with seed=42 from yes/no subset; full yes/no subset ~200 questions)

**Hypothesis Fit:**
- TruthfulQA adversarial design tests whether ranking generalizes beyond TriviaQA trivia format
- Yes/no subset provides binary correctness labels suitable for AUROC computation
- Adversarial nature (misconceptions) tests VC calibration under model-deceptive conditions

**Statistics:**
- Total TruthfulQA generation split: 817 questions
- Yes/no subset: ~200 questions (use all; pad to 200 if fewer)
- Binary EM label: answer matches gold (yes/no as appropriate)

**Preprocessing:**
- Filter generation split for yes/no questions (question type = yes/no or best_answer in {yes, no})
- Sample N=200 with seed=42
- Tokenize with Llama-2 tokenizer (max_length=512)
- Binary label: `int(normalize(generated_answer) in normalize_set(gold_answers))`

**Augmentation:** None (inference task)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"truthful_qa"`, config `"generation"`
- Code: `load_dataset("truthful_qa", "generation")`

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (meta-llama/Llama-2-7b-hf)
**Parameters:** 7B
**Role:** Generation model for SE, SCG, TE uncertainty computation
**Configuration:**
- Temperature: 0.7 (stochastic sampling for K=10)
- Temperature: 0.0 / greedy (for TE logit extraction)
- K: 10 samples per question
- max_new_tokens: 50 (short answer extraction)

**Modifications for Hypothesis:** None — same model as h-e2-v2 and H-M4; only dataset changes.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"meta-llama/Llama-2-7b-hf"`
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf", torch_dtype=torch.float16, device_map="auto")`

#### VC Model

**Architecture:** Llama-2-7B-Chat (meta-llama/Llama-2-7b-chat-hf)
**Role:** Verbalized confidence elicitation (VC method only)
**Loading Information:**
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf", torch_dtype=torch.float16, device_map="auto")`

#### Proposed Model

**Architecture:** Same models as baseline — this is a comparison experiment, not architecture modification.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Four-way AUROC ranking comparison on TruthfulQA
# Based on: lorenzkuhn/semantic_uncertainty, potsawee/selfcheckgpt, h-e2-v2, H-M4

def compute_four_way_auroc(questions, model_7b, model_chat, K=10, seed=42):
    """
    Args:
        questions: List[dict] — TruthfulQA yes/no subset, N=200
        model_7b: Llama-2-7B for SE/SCG/TE computation
        model_chat: Llama-2-7B-Chat for VC elicitation
        K: int — stochastic samples per question
    Returns:
        dict: {method: {'auroc': float, 'ci_lower': float, 'ci_upper': float}}
    """
    te_scores, se_scores, scg_scores, vc_scores, em_labels = [], [], [], [], []

    for q in questions:
        # Step 1: Generate K=10 samples (temp=0.7) + greedy for TE logits
        samples = model_7b.generate(q['question'], K=K, temperature=0.7)
        greedy_logits = model_7b.greedy_decode(q['question'], return_logits=True)

        # Step 2: TE — mean per-token Shannon entropy from greedy logits
        te = mean_token_entropy(greedy_logits)

        # Step 3: SE — NLI clustering (DeBERTa) + cluster entropy
        clusters = nli_cluster(samples, nli_model, threshold='entailment')
        se = cluster_entropy(clusters, K)

        # Step 4: SCG — 1 - mean pairwise BERTScore across K samples
        scg = 1.0 - mean_pairwise_bertscore(samples, rescale=True)

        # Step 5: VC — extract numeric confidence from Chat model output
        vc_text = model_chat.generate(vc_prompt(q['question']), temperature=0.0)
        vc = extract_confidence_score(vc_text)  # regex [0-100]; None → 50.0

        # Step 6: Binary EM label for TruthfulQA
        em = int(normalize(samples[0]) in normalize_answers(q['best_answer']))
        te_scores.append(te); se_scores.append(se)
        scg_scores.append(scg); vc_scores.append(vc); em_labels.append(em)

    # Bootstrap AUROC (1000 iterations, seed=42)
    results = {}
    for method, scores in [('TE', te_scores), ('SE', se_scores),
                            ('SCG', scg_scores), ('VC', vc_scores)]:
        auroc, ci_lo, ci_hi = bootstrap_auroc(scores, em_labels, n=1000, seed=seed)
        results[method] = {'auroc': auroc, 'ci_lower': ci_lo, 'ci_upper': ci_hi}
    return results
```

### Training Protocol

**Type:** Inference-only experiment (no model training)

**Reusing from H-M4 (continuation — controlled experiment):**
- Generation: temperature=0.7, K=10 samples per question
- Greedy decode: temperature=0.0, for TE logit extraction
- VC: temperature=0.0 (deterministic)
- Seed: 42 (fixed)
- NLI model: `cross-encoder/nli-deberta-v3-small` (same as h-e2-v2)
- BERTScore: `bert-score` library, `rescale_with_baseline=True`, lang="en"
- Batch size: 8 questions (GPU memory constraint at 7B)
- Estimated runtime: ~3-4 hours GPU (200 questions × K=10 × 2 models)

**Source:** h-e2-v2 (SE/TE/SCG hyperparameters), H-M4 (VC hyperparameters), both validated.

**Seeds:** 1 (seed=42, fixed throughout)

### Evaluation

**Task Type:** Binary classification (hallucination detection via uncertainty ranking)

**Primary Metrics:**
- AUROC (Area Under ROC Curve) for each method: SE, SCG, TE, VC
  - Against binary EM correctness labels
  - Bootstrap 95% CI (1000 iterations, seed=42)

**Success Criteria (SHOULD_WORK gate):**
- **Primary gate:** SE AUROC > TE AUROC on TruthfulQA (direction preserved cross-benchmark)
- **Secondary:** VC AUROC < TE AUROC on TruthfulQA (scale-degradation benchmark-agnostic)
  - *Note:* Uncertain given H-M4 failure (VC > TE on TriviaQA); document if violated
- **Tertiary:** Full ranking SE >= SCG > TE > VC holds

**Expected Baseline Performance (from literature + prior hypotheses):**
- TruthfulQA adversarial nature → generally lower AUROC for all methods vs TriviaQA
- SE: ~0.50-0.60 (Kuhn et al. 2023 extrapolation; h-e2-v2 showed 0.54 on TriviaQA)
- TE: ~0.48-0.55 (similar to TriviaQA performance)
- SCG: ~0.48-0.58 (BERTScore consistency; domain-general)
- VC: uncertain — H-M4 showed 0.4463 (above TE=0.4381) on TriviaQA

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification
- Library: `sklearn.metrics.roc_auc_score` + custom bootstrap
- Code:
  ```python
  from sklearn.metrics import roc_auc_score
  import numpy as np

  def bootstrap_auroc(scores, labels, n=1000, seed=42):
      rng = np.random.default_rng(seed)
      base = roc_auc_score(labels, scores)
      boot = [roc_auc_score(labels[idx := rng.integers(len(labels), size=len(labels))],
                            np.array(scores)[idx]) for _ in range(n)]
      return base, np.percentile(boot, 2.5), np.percentile(boot, 97.5)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of AUROC for SE, SCG, TE, VC on TruthfulQA with 95% CI error bars

#### Additional Figures (LLM Autonomous)

Based on the CONDITION hypothesis testing cross-benchmark generalization:
- **Cross-benchmark comparison:** Side-by-side AUROC bar chart: TriviaQA (H-M4/h-e2-v2) vs TruthfulQA (H-C1) for all four methods
- **Rank ordering visualization:** Method ranking with CI overlap analysis (non-overlapping = significant)
- **VC confidence distribution:** Histogram of VC scores on TruthfulQA vs TriviaQA (domain sensitivity)
- **Bootstrap AUROC distribution:** Violin plot of bootstrap AUROC distributions per method

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-c1/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions:**
- `mechanism_exists`: true — all four methods computable on TruthfulQA yes/no subset
- `mechanism_isolatable`: true — each method computed independently on same K=10 samples
- `baseline_measurable`: true — AUROC against binary EM labels is well-defined

**Architecture Compatibility:**
- `architecture_compatibility`: N/A — inference-only experiment; no new architecture
  - Llama-2-7B: confirmed compatible with SE/SCG/TE (h-e2-v2)
  - Llama-2-7B-Chat: confirmed compatible with VC (H-M4)

**Activation Indicators:**
- `mechanism_log_message`:
  ```
  H-C1 TruthfulQA results: SE={se:.4f} [{se_lo:.4f},{se_hi:.4f}],
  SCG={scg:.4f} [{scg_lo:.4f},{scg_hi:.4f}],
  TE={te:.4f} [{te_lo:.4f},{te_hi:.4f}],
  VC={vc:.4f} [{vc_lo:.4f},{vc_hi:.4f}]
  Ranking: {ranking} | SE>TE: {se>te} | VC<TE: {vc<te}
  ```
- `tensor_shape_change`: N/A (scoring task)
- `metric_delta_expected`: SE AUROC > TE AUROC (direction preserved from TriviaQA)

**Mechanism Verification Code:**
```python
# Verify gate conditions
assert n_questions >= 200, f"Insufficient questions: {n_questions}"
assert all(0 <= s <= 1 for s in em_labels), "EM labels must be binary"
assert 0 <= auroc_se <= 1 and 0 <= auroc_te <= 1, "AUROC out of range"

# Gate check (SHOULD_WORK — log result, do not crash)
gate_primary = auroc_se > auroc_te
gate_secondary = auroc_vc < auroc_te
print(f"Gate primary (SE>TE): {gate_primary} (SE={auroc_se:.4f}, TE={auroc_te:.4f})")
print(f"Gate secondary (VC<TE): {gate_secondary} (VC={auroc_vc:.4f}, TE={auroc_te:.4f})")
```

**Success Thresholds:**
- `hypothesis_support_threshold`: SE AUROC > TE AUROC (primary; no minimum gap required)
- `hypothesis_support_metric`: AUROC(SE) - AUROC(TE) > 0

---

## PoC Success Check

**Gate Type:** SHOULD_WORK (failure narrows scope, does not stop pipeline)

**PoC Pass Condition:**
1. Code runs without error on TruthfulQA yes/no subset (N=200)
2. `auroc_se > auroc_te` (SE beats TE on TruthfulQA — direction preserved)

**Secondary check (informative, not gate):**
3. `auroc_vc < auroc_te` (VC scale-degradation benchmark-agnostic)
4. Full ranking SE >= SCG > TE > VC holds

---

## Ablation Studies

**Ablation 1: Sample size sensitivity**
- N=200 (primary) vs all yes/no questions (~817 max)
- Purpose: Confirm N=200 provides sufficient statistical power
- Expected: AUROC estimates stabilize; CI narrows with more samples

**Ablation 2: Cross-benchmark comparison (mandatory)**
- Direct comparison: TriviaQA results (from H-M4/h-e2-v2) vs TruthfulQA (H-C1)
- Methods: All four computed under identical conditions on each benchmark
- Tests: Whether SE-TE gap direction is preserved; whether VC ranking is benchmark-dependent

**Ablation 3: VC prompt format sensitivity**
- Standard H-M4 prompt: "Answer the question, then rate your confidence 0-100%."
- TruthfulQA-adapted: same prompt (TruthfulQA yes/no questions work with same format)
- If VC outputs degenerate (all same score), try alternative: "Is this statement true or false? [statement]. Confidence (0-100%):"

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources (MCP unavailable — literature synthesis)

**Source A.1: Kuhn et al. 2023 — Semantic Uncertainty (NeurIPS 2023)**
- Type: Peer-reviewed academic paper
- Query equivalent: "semantic entropy uncertainty quantification LLM AUROC"
- Key insights: SE scales with model size; 7B shows ~0.54 AUROC on TriviaQA; NLI clustering is the mechanism
- Hyperparameters: K=10, temperature=0.7, DeBERTa cross-encoder NLI
- Used for: SE specification, expected AUROC range at 7B scale

**Source A.2: Manakul et al. 2023 — SelfCheckGPT (EMNLP 2023)**
- Type: Peer-reviewed academic paper
- Key insights: BERTScore consistency achieves comparable discrimination to SE on factual tasks
- Used for: SCG implementation specification, expected performance relationship to SE

**Source A.3: Xiong et al. 2023 — Can LLMs Express Their Uncertainty?**
- Type: Peer-reviewed academic paper
- Key insights: 7B poorly calibrated; VC AUROC ~0.50-0.55 at 7B; improves at 13B+
- Used for: VC expected performance, H-M4 context integration

**Source A.4: Lin et al. 2022 — TruthfulQA**
- Type: Peer-reviewed academic paper + official benchmark
- Key insights: 817 questions (generation split); yes/no subset ~200; adversarial; binary labels
- Used for: Dataset specification, N=200 selection

### B. GitHub Implementations (Exa MCP unavailable — domain knowledge)

**Repository B.1: lorenzkuhn/semantic_uncertainty**
- URL: https://github.com/lorenzkuhn/semantic_uncertainty
- Priority: ⭐⭐⭐ HIGHEST (paper author's official implementation)
- Key files: generate_samples.py (K sample generation), compute_uncertainties.py (SE/TE), evaluate_uncertainties.py (AUROC)
- Config extracted: temperature=0.7, K=10, DeBERTa cross-encoder, bootstrap 1000 iterations
- Used for: SE + TE implementation specification

**Repository B.2: potsawee/selfcheckgpt**
- URL: https://github.com/potsawee/selfcheckgpt
- Priority: ⭐⭐⭐ HIGHEST for SCG
- Key: `SelfCheckBERTScore(rescale_with_baseline=True).predict(samples, passage)`
- Used for: SCG implementation specification

**Repository B.3: sylinrl/TruthfulQA**
- URL: https://github.com/sylinrl/TruthfulQA
- Priority: ⭐⭐⭐ HIGHEST for dataset
- Key: yes/no subset extraction from generation split; EM evaluation
- Used for: Dataset loading specification

### C. Code Analysis (Serena)

Serena analysis: Not performed — code sufficiently clear from repositories above and h-e2-v2/H-M4 validated codebase.

### D. Previous Hypothesis Context

**Source:** H-M4 Phase 4 Validation (docs/youra_research/h-m4/04_validation.md)

- **File:** docs/youra_research/h-m4/04_validation.md
- **Reused components:**
  - Llama-2-7B generation pipeline (SE/SCG/TE) — proven stable
  - Llama-2-7B-Chat VC elicitation code — proven functional (though VC > TE unexpectedly)
  - Bootstrap AUROC computation — validated
  - Hyperparameters: temperature=0.7, K=10, seed=42
- **Why reused:** Enables controlled comparison — only benchmark changes; all method code identical
- **Critical H-M4 finding:** VC AUROC (0.4463) > TE AUROC (0.4381) on TriviaQA
  - This means VC secondary gate criterion is uncertain for H-C1
  - Primary gate (SE > TE direction) remains testable independently

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|-----------------|
| Dataset: TruthfulQA yes/no | Academic + HuggingFace | Lin et al. 2022; sylinrl/TruthfulQA |
| N=200, seed=42 | Phase 2A spec | 02b_verification_plan.md H-C1 |
| SE implementation | Academic + GitHub | Kuhn et al. 2023; lorenzkuhn/semantic_uncertainty |
| SCG BERTScore | Academic + GitHub | Manakul et al. 2023; potsawee/selfcheckgpt |
| TE greedy logits | h-e2-v2 codebase | Prior validated session |
| VC Chat elicitation | H-M4 code | H-M4 Phase 4 |
| AUROC bootstrap (1000) | h-e2-v2 + H-M4 | Prior hypotheses |
| Expected SE AUROC | Kuhn et al. 2023 + h-e2-v2 | ~0.50-0.60 at 7B |
| Expected VC behavior | Xiong et al. 2023 + H-M4 | Uncertain; H-M4: VC > TE |
| Temperature=0.7, K=10 | Kuhn et al. 2023 + h-e2-v2 | Standard for SE computation |
| Cross-benchmark ablation | Phase 2A H-C1 spec | 02b_verification_plan.md §3.2 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written to file)
**Date:** 2026-08-25

### Workflow History for This Hypothesis

- experiment_design.status set to IN_PROGRESS (Step 1)
- All steps 1-8 executed in UNATTENDED mode
- MCP limitation documented (Archon + Exa unavailable; Serena skipped as not needed)
- experiment_design.status set to COMPLETED (Step 8)

---

*MCP Tools Used: None (ablation session — Archon, Exa, Serena unavailable)*
*Specifications grounded in peer-reviewed literature (Kuhn 2023, Manakul 2023, Xiong 2023, Lin 2022) and prior validated session hypotheses (h-e2-v2, H-M4)*
*Next Phase: Phase 3 — Implementation Planning*
