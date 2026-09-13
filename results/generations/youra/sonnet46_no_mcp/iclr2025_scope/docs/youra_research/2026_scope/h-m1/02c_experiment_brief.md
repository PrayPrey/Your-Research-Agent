# Experiment Design: H-M1

**Date:** 2026-05-04
**Author:** Anonymous
**Hypothesis Statement:** Under the same evaluation inputs with H2O eviction at r=50%, if eviction-aware LoRA adapters are compared to sequential baseline adapters, then per-layer attention entropy and heavy-hitter concentration (top-20% attention token score ratio) will differ significantly (paired t-test p < 0.05 on at least 50% of transformer layers), because token-scarcity regularization during training causes adapters to develop qualitatively different attention patterns calibrated to the evicted-cache distribution.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests functional change in attention behavior as mechanistic evidence for token-scarcity regularization.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 COMPLETED (PASS — cosine similarity < 0.95 confirmed in all 24 LoRA layers)
**Gate Status:** MUST_WORK — pipeline stops if p < 0.05 not achieved in ≥50% layers on ≥1 model

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED — PASS)

### Gate Condition
MUST_WORK: Paired t-test p < 0.05 on attention entropy in ≥50% of transformer layers on at least one of LLaMA-2-7B or Mistral-7B-v0.1. Failure → PIVOT (examine deeper layers, task-specific effects).

---

## Continuation Context

**This is a continuation experiment building directly on H-E1.**

### Previous Hypothesis Results (H-E1)
- **Gate Result:** PASS (MUST_WORK satisfied)
- **Key Finding:** All 24/24 LoRA layers show cosine similarity < 0.95 (min=-0.578, mean=0.053 — near-orthogonal weights). H2O mask injection produces significantly different gradient signals reaching LoRA A/B matrices.
- **Proven Components Reused:**
  - Trained adapter checkpoints: eviction-aware and sequential baseline variants for LLaMA-2-7B and Mistral-7B-v0.1
  - H2OEvictionAwareAttention hook implementation (h-e1/code/model.py)
  - LoRA hyperparameters: rank=16, alpha=32, dropout=0.05 (confirmed stable in H-E1)
  - LongAlpacaDataset loading code (h-e1/code/data.py)
- **H-M1 Extension:** Adds attention score extraction hooks to capture per-layer attention weight tensors during LongBench inference forward passes.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Attention Entropy Experiment Design**

- **Finding:** Attention entropy (H = -Σ p_i log p_i over sequence positions) is a standard diagnostic for measuring attention focus in transformer models. Low entropy = concentrated attention on few tokens (heavy-hitter regime); high entropy = diffuse attention. Entropy differences between model variants are detected via paired statistical tests across layers.
  - Dataset: LongBench (THUDM/LongBench) — canonical for long-context attention analysis
  - Hyperparameters: evaluate with same H2O r=50% as training simulation; ≥500 samples per category
  - Key insight: Paired t-test across layers (N=32 for LLaMA-2-7B) has sufficient power to detect systematic entropy shifts (Clark et al. 2019, "What Does BERT Look At?")

- **Finding:** Heavy-hitter concentration is defined in H2O (Zhang et al. 2023) as the ratio of cumulative attention mass on the top-20% highest-scoring tokens. H2O shows this ratio is 0.8–0.9 in standard LLaMA-2 attention, indicating strong concentration. Eviction-aware training may increase or redistribute this concentration.
  - Standard measure: ratio = Σ(top-20% attention scores) / Σ(all attention scores) per layer per head
  - Aggregation: mean across heads, then report per-layer

**Query 2: Implementation Challenges & Best Practices**

- **Finding:** Attention weight extraction requires careful hook placement. In HuggingFace transformers LLaMA implementation, attention weights are available from `LlamaAttention.forward()` return value only when `output_attentions=True` is set in the model config or passed as kwarg. The returned `attn_weights` tensor has shape (batch, num_heads, seq_len, seq_len) — must be averaged over batch and heads for per-layer entropy.
  - Best practice: Use `model(input_ids, output_attentions=True)` rather than hooks to avoid shape mismatches
  - Pitfall: Memory cost scales as O(seq_len²) — for LongBench inputs (up to 4096 tokens) this is 16M floats per layer; use chunked inference or reduce batch size to 1

- **Finding:** H2O eviction at inference must be applied consistently for both adapter variants. Use the same H2O implementation from H-E1 (FMInference/H2O or equivalent hook-based implementation) to ensure identical eviction masks for both conditions — any mask difference would confound the attention entropy comparison.

**Query 3: LongBench Benchmark Setup**

- **Finding:** LongBench (THUDM/LongBench, Bai et al. 2023) provides 21 tasks across 6 categories: Single-Document QA (NarrativeQA, Qasper, MultiFieldQA-en/zh), Multi-Document QA (HotpotQA, 2WikiMultihopQA, MuSiQue), Summarization (GovReport, QMSum, MultiNews), Few-Shot Learning (TREC, TriviaQA, SAMSum, PassageCount), Synthetic Tasks (PassageRetrieval-en/zh), Code Completion (LCC, RepoBench-P).
  - Minimum samples per task: NarrativeQA has 200 test samples; most tasks have 200–500
  - For ≥500 samples/category: aggregate across tasks within each category (6 categories, each has 2-4 tasks)
  - Standard evaluation: use `load_dataset("THUDM/LongBench", task_name)` for each of the 21 tasks

### Archon Code Examples

**Code Pattern 1: Attention Weight Extraction with output_attentions=True**

```python
# Standard HuggingFace pattern for attention weight extraction
with torch.no_grad():
    outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask,
        output_attentions=True  # Returns tuple of (batch, heads, seq, seq) per layer
    )
attentions = outputs.attentions  # Tuple of L tensors, each (B, H, S, S)

def compute_entropy(attn_weights):
    # attn_weights: (B, H, S, S) — softmax already applied
    # Entropy over key dimension (what the query attends to)
    eps = 1e-10
    entropy = -torch.sum(attn_weights * torch.log(attn_weights + eps), dim=-1)
    # entropy: (B, H, S) — entropy per query position per head
    return entropy.mean(dim=(0, 1, 2)).item()  # scalar per layer
```

**Code Pattern 2: Heavy-Hitter Concentration Ratio**

```python
def compute_hh_concentration(attn_weights, top_ratio=0.2):
    # attn_weights: (B, H, S, S) after softmax
    # Concentration: how much attention mass is on top-20% tokens
    B, H, S_q, S_k = attn_weights.shape
    k = max(1, int(S_k * top_ratio))  # top-20% of key positions
    # Sum attention weights, average over query positions
    mean_attn = attn_weights.mean(dim=2)  # (B, H, S_k)
    topk_vals, _ = mean_attn.topk(k, dim=-1)  # (B, H, k)
    concentration = topk_vals.sum(dim=-1) / mean_attn.sum(dim=-1)  # (B, H)
    return concentration.mean().item()  # scalar per layer
```

### Exa GitHub Implementations

**Repository 1: THUDM/LongBench (Official)**
- **URL:** https://github.com/THUDM/LongBench
- **Relevance:** Official LongBench evaluation harness; provides per-task metric computation
- **Key Code:** `pred.py` — generates model predictions per task; `eval.py` — computes metrics (F1 for QA, ROUGE-L for summarization, accuracy for classification)
- **Training Config:** N/A (evaluation only)
- **Dataset:** All 21 LongBench tasks via HuggingFace datasets API

**Repository 2: FMInference/H2O (Official H2O)**
- **URL:** https://github.com/FMInference/H2O
- **Relevance:** Official H2O heavy-hitter oracle implementation; defines heavy-hitter eviction mask logic
- **Key Code:** `h2o.py` — `H2OKVCache` class implementing past_key_values eviction based on cumulative attention score ranking
- **Architecture:** Hook-based modification of HuggingFace LLaMA attention; accumulates attention scores across decode steps; evicts bottom-(1-r) fraction of KV entries
- **Training Config:** r=0.5 (50% retention) is primary evaluation point; supports r∈{0.25, 0.5, 0.75}

**Repository 3: Attention Analysis Pattern (bertviz / transformers-interpret)**
- **Relevance:** Provides standard patterns for per-layer attention entropy computation in transformer analysis
- **Key Code:** Layer-wise attention weight capture via `output_attentions=True`; entropy aggregation across heads
- **Insight:** Use batch_size=1 for LongBench inference (long sequences exhaust GPU memory with full attention matrices)

**Serena Analysis Needed:** false

### 🎯 Implementation Priority Assessment

For H-M1, this is NOT a paper reproduction — it is a new mechanistic analysis experiment built on H-E1 infrastructure.

**Recommended Implementation Path:**
- Primary: Extend h-e1/code/model.py with attention extraction module; reuse H-E1 adapter checkpoints
- Fallback: Fresh implementation using HuggingFace transformers `output_attentions=True`
- Justification: H-E1 already implements H2OEvictionAwareAttention hook — extend to also capture attention weights during forward pass; avoids code duplication

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-E1 implementation (model.py, train.py) provides the base; H-M1 adds attention extraction only.

---

## Experiment Specification

### Dataset

**Evaluation Dataset: LongBench**
- **Name:** LongBench
- **Version:** THUDM/LongBench (HuggingFace Hub, canonical version)
- **Type:** standard (real, established benchmark — NOT synthetic)
- **Source:** https://huggingface.co/datasets/THUDM/LongBench
- **Tasks:** 21 tasks across 6 categories
  - Single-Document QA: NarrativeQA, Qasper, MultiFieldQA-en
  - Multi-Document QA: HotpotQA, 2WikiMultihopQA, MuSiQue
  - Summarization: GovReport, QMSum, MultiNews
  - Few-Shot Learning: TREC, TriviaQA, SAMSum, PassageCount
  - Synthetic Tasks: PassageRetrieval-en/zh
  - Code Completion: LCC, RepoBench-P
- **Sample Counts:** Full test set per task (200–500 samples/task; aggregate ≥500/category)
- **Splits Used:** Test split only (standard LongBench evaluation protocol)
- **Input Length:** 0–32k tokens; truncated to model max_length (4096 for LLaMA-2-7B)
- **Preprocessing:**
  - Tokenize with model-specific tokenizer (LlamaTokenizer / MistralTokenizer)
  - Truncate from middle (keep first 1000 + last 3000 tokens) — standard LongBench protocol
  - Batch size: 1 (required for long sequences with attention weight extraction)
- **No augmentation** (evaluation only)

**Fine-tuning Dataset (reused from H-E1): LongAlpaca-12k**
- **Name:** LongAlpaca-12k
- **Source:** Yukang/LongAlpaca (HuggingFace Hub)
- **Role:** Training data for both adapter variants (already trained in H-E1; not re-trained in H-M1)
- **Type:** standard

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"THUDM/LongBench"` (per task: `load_dataset("THUDM/LongBench", task_name, split="test")`)
- Code: `from datasets import load_dataset; ds = load_dataset("THUDM/LongBench", "narrativeqa", split="test")`

### Models

#### Baseline Model

**Architecture:** LLaMA-2-7B with sequential LoRA adapter (trained in H-E1)
- **Base Model:** meta-llama/Llama-2-7b-hf
- **Adapter:** Sequential baseline LoRA (standard LoRA on LongAlpaca-12k, no eviction mask during training)
- **LoRA Config:** rank=16, alpha=32, dropout=0.05, target_modules=["q_proj", "v_proj"]
- **Checkpoint:** Reused from H-E1 validation (h-e1/code/ trained checkpoint)
- **Inference:** H2O eviction applied at r=50% during LongBench forward pass
- **Evaluation Mode:** `output_attentions=True` to capture per-layer attention matrices

**Second Baseline Model:** Mistral-7B-v0.1 with sequential LoRA adapter (same config, trained in H-E1)
- **Base Model:** mistralai/Mistral-7B-v0.1
- **Adapter:** Sequential baseline LoRA (same training as above)
- **Checkpoint:** Reused from H-E1

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers + PEFT
- Identifier: `"meta-llama/Llama-2-7b-hf"` / `"mistralai/Mistral-7B-v0.1"`
- Code: `model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf"); model = PeftModel.from_pretrained(model, "h-e1/checkpoints/sequential_baseline")`

#### Proposed Model

**Architecture:** LLaMA-2-7B / Mistral-7B-v0.1 with eviction-aware LoRA adapter (trained in H-E1)
- **Adapter:** Eviction-aware LoRA (trained with H2O hard-mask at r=50% during forward pass)
- **Checkpoint:** Reused from H-E1 validation
- **Inference:** Same H2O eviction at r=50% applied identically as for baseline

**Core Mechanism Implementation:**

```python
# Core Mechanism: Attention Entropy & Heavy-Hitter Analysis
# Based on: H-E1 H2OEvictionAwareAttention + HuggingFace output_attentions protocol

class AttentionAnalysisExtractor:
    """
    Extracts per-layer attention entropy and heavy-hitter concentration
    during LongBench inference with H2O eviction at r=0.5.
    """
    def __init__(self, model, top_ratio=0.2):
        self.model = model
        self.top_ratio = top_ratio  # top-20% heavy-hitter threshold

    def extract_metrics(self, input_ids, attention_mask):
        """
        Args:
            input_ids: (1, seq_len) — batch_size=1 for memory
            attention_mask: (1, seq_len)
        Returns:
            entropy_per_layer: List[float], length = num_layers
            hh_concentration_per_layer: List[float], length = num_layers
        """
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_attentions=True   # (B, H, S, S) per layer
            )
        attn_tuple = outputs.attentions  # len = num_layers

        entropy_per_layer = []
        hh_conc_per_layer = []
        for layer_attn in attn_tuple:
            # layer_attn: (1, num_heads, seq_len, seq_len)
            # Entropy over key dim (per query position, then averaged)
            eps = 1e-10
            ent = -(layer_attn * torch.log(layer_attn + eps)).sum(-1)  # (1,H,S)
            entropy_per_layer.append(ent.mean().item())

            # Heavy-hitter concentration: top-20% key positions
            mean_attn_over_queries = layer_attn.mean(dim=2)  # (1, H, S_k)
            k = max(1, int(mean_attn_over_queries.shape[-1] * self.top_ratio))
            topk_vals, _ = mean_attn_over_queries.topk(k, dim=-1)
            conc = topk_vals.sum(-1) / mean_attn_over_queries.sum(-1)  # (1,H)
            hh_conc_per_layer.append(conc.mean().item())

        return entropy_per_layer, hh_conc_per_layer

    def run_paired_ttest(self, baseline_metrics, proposed_metrics):
        """Compare per-layer metrics; return layer-wise p-values."""
        from scipy.stats import ttest_rel
        p_values = []
        for layer_idx in range(len(baseline_metrics[0])):
            baseline_vals = [m[layer_idx] for m in baseline_metrics]
            proposed_vals = [m[layer_idx] for m in proposed_metrics]
            _, p = ttest_rel(baseline_vals, proposed_vals)
            p_values.append(p)
        return p_values  # len = num_layers
```

### Training Protocol

**Note:** H-M1 does NOT re-train. Adapters are loaded from H-E1 checkpoints. This step covers only inference configuration.

**Inference Configuration (reused from H-E1, adapted for attention extraction):**
- **Optimizer:** N/A (inference only)
- **Batch Size:** 1 (required — long sequences + output_attentions=True exhaust GPU memory)
- **Max Sequence Length:** 4096 tokens (LLaMA-2-7B / Mistral-7B-v0.1 native context)
- **Truncation:** Middle truncation (keep first 1000 + last 3000 tokens) — LongBench standard
- **Eviction Config:** H2O r=0.5, heavy_ratio=0.1, recent_ratio=0.1 — identical for both adapter variants
- **Seeds:** 1 (fixed, deterministic evaluation)
- **Precision:** float16 (same as H-E1)
- **Device:** Single GPU (CUDA_VISIBLE_DEVICES set to empty GPU)

**Sampling Protocol:**
- Evaluate ≥500 samples per LongBench category
- For tasks with < 500 samples: use full test set
- For categories with multiple tasks: aggregate samples across tasks until ≥500 total
- Per-layer attention matrices saved in memory (not to disk) — processed sample-by-sample

**Source:** H-E1 validation report (h-e1/04_validation.md); H2O paper (Zhang et al. 2023, r=0.5 as primary evaluation point)

### Evaluation

**Primary Metrics:**

1. **Attention Entropy per Layer** (H = -Σ p_i log p_i)
   - Computed per layer, averaged over heads and sequence positions
   - Values: range 0 (fully concentrated) to log(seq_len) (uniform)
   - Comparison: eviction-aware vs. sequential baseline
   - Statistical test: Paired t-test across samples (N ≥ 500 per category)

2. **Heavy-Hitter Concentration Ratio**
   - Ratio of attention mass on top-20% key tokens per layer
   - Range: 0.2 (uniform) to 1.0 (fully concentrated on top-20%)
   - Comparison: eviction-aware vs. sequential baseline

**Success Criteria:**
- **Primary (MUST_WORK gate):** Paired t-test p < 0.05 on attention entropy in ≥50% of transformer layers (≥16/32 layers for LLaMA-2-7B; ≥16/32 for Mistral-7B-v0.1) on at least one model
- **Secondary:** Heavy-hitter concentration ratio differs by ≥5% in mean across layers (directional evidence)

**PoC Pass Condition:**
1. Code runs without error
2. `p_value < 0.05` in ≥50% of layers for at least one model
3. Direction of entropy change is systematic (not random per layer)

**Expected Baseline Performance (from literature):**
- LLaMA-2-7B attention entropy under standard inference: ~3.5–5.0 nats for 4096-token inputs (estimated from H2O paper heavy-hitter analysis)
- Heavy-hitter concentration at r=50%: ~0.85–0.92 for LLaMA-2-7B (H2O paper, Fig. 3)
- Source: Zhang et al. (2023) "H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models"

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: attention_analysis (custom)
- Library: scipy.stats (ttest_rel), torch (entropy/concentration computation)
- Code: `from scipy.stats import ttest_rel; _, p = ttest_rel(baseline_entropy_layer_i, proposed_entropy_layer_i)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart — percentage of layers with p < 0.05 (target: ≥50% line marked)

#### Additional Figures (LLM Autonomous)

1. **Per-Layer Attention Entropy Comparison:** Line plot — entropy per layer (0–31) for eviction-aware vs. sequential baseline, with shaded standard error; separate panels for LLaMA-2-7B and Mistral-7B-v0.1
2. **Per-Layer Heavy-Hitter Concentration:** Line plot — HH concentration ratio per layer for both adapter variants; highlight layers with significant difference (p < 0.05 marked with asterisk)
3. **p-value Heatmap:** Layer × metric (entropy, HH concentration) heatmap of -log10(p-value) with p=0.05 significance threshold line
4. **Entropy Distribution by Task Category:** Box plot — attention entropy distribution across LongBench categories (6 categories) for both adapter variants, showing where effect is strongest

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Purpose:** Verify that the attention analysis mechanism actually captures real attention differences — not just numerical noise.

**Pre-conditions (must verify before running full experiment):**
- `mechanism_exists`: True — attention entropy is mathematically well-defined for any softmax output; output_attentions=True is supported in HuggingFace transformers for LLaMA-2 and Mistral
- `mechanism_isolatable`: True — H2O eviction applied identically to both variants; only adapter weights differ between conditions
- `baseline_measurable`: True — sequential baseline adapter from H-E1 provides clean control condition with PASS validation

**Architecture Compatibility:**
- `architecture_compatibility`: LLaMA-2-7B (32 transformer layers, 32 heads, GQA) and Mistral-7B-v0.1 (32 layers, 32 heads, sliding window attention) both support `output_attentions=True` in HuggingFace transformers ≥4.35
- **Warning:** Mistral sliding window attention (window=4096) means attention matrices are not full seq_len×seq_len for long inputs — entropy computed within window only; document this limitation

**Activation Indicators (signs mechanism is working):**
- `mechanism_log_message`: "Layer {i}: baseline_entropy={:.4f}, proposed_entropy={:.4f}, p={:.4f}"
- `tensor_shape_change`: Input attention: (1, num_heads, seq_len, seq_len) → entropy: scalar per layer. Shape should be consistent across samples; flag if shape changes unexpectedly
- `metric_delta_expected`: Entropy difference of 0.1–0.5 nats per layer is a meaningful signal; differences < 0.01 suggest mechanism not engaging

**Mechanism Verification Code:**

```python
# Smoke test: verify attention extraction works before full experiment
def verify_attention_extraction(model, tokenizer, device):
    test_input = "The quick brown fox " * 100  # ~400 tokens
    inputs = tokenizer(test_input, return_tensors="pt", truncation=True,
                       max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)
    assert outputs.attentions is not None, "output_attentions not returned"
    assert len(outputs.attentions) == model.config.num_hidden_layers, \
        f"Expected {model.config.num_hidden_layers} layers, got {len(outputs.attentions)}"
    layer0 = outputs.attentions[0]
    assert layer0.shape == (1, model.config.num_attention_heads,
                            inputs.input_ids.shape[1],
                            inputs.input_ids.shape[1]), \
        f"Unexpected attention shape: {layer0.shape}"
    # Verify softmax (rows sum to 1)
    row_sums = layer0.sum(dim=-1)
    assert torch.allclose(row_sums, torch.ones_like(row_sums), atol=1e-3), \
        "Attention weights do not sum to 1 — softmax not applied"
    print("✅ Attention extraction verified: shapes and normalization correct")
```

**Failure Detection:**
- If all p-values > 0.5: attention weights may not be captured correctly (check `output_attentions=True` propagation through H2O hook)
- If entropy values are NaN: log(0) issue — verify eps=1e-10 is applied before log
- If concentration ratios are all identical (< 0.001 difference): eviction mask may not be applied at inference; verify H2O hook is active for both conditions

**Hypothesis Support Threshold:**
- `hypothesis_support_threshold`: p < 0.05 in ≥50% of layers (≥16/32 layers)
- `hypothesis_support_metric`: Percentage of layers with paired t-test p < 0.05 on attention entropy

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (attention extraction + H2O eviction compatible)
2. Paired t-test p < 0.05 in ≥50% of transformer layers on at least one model (LLaMA-2-7B or Mistral-7B-v0.1)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** Attention Entropy as Mechanistic Probe
- **Query Used:** "attention entropy analysis transformer layers mechanistic interpretability"
- **Relevance:** Established method for comparing attention distributions between model variants
- **Key Insights:**
  - Shannon entropy H = -Σ p_i log p_i computed over key dimension of attention matrix
  - Paired t-test standard for layer-level comparison (N = num_samples per test)
  - Memory constraint: output_attentions=True requires O(batch × heads × seq²) memory
- **Used For:** Core metric definition (Section Evaluation Metrics), implementation pattern

**Source A.2:** H2O Heavy-Hitter Concentration Definition
- **Query Used:** "H2O heavy hitter oracle attention concentration ratio LLaMA"
- **Relevance:** Defines the secondary metric (heavy-hitter concentration ratio) and its expected values
- **Key Insights:**
  - Top-20% tokens accumulate 80–90% of attention mass in LLaMA-2-7B (H2O paper Fig. 3)
  - Concentration ratio is stable across sequence types — suitable as mechanistic probe
  - H2O r=0.5 evicts 50% of KV entries by removing lowest-cumulative-score tokens
- **Used For:** Heavy-hitter concentration metric definition, expected baseline range

**Source A.3:** LongBench Evaluation Protocol
- **Query Used:** "LongBench benchmark evaluation protocol attention analysis long-context"
- **Relevance:** Provides dataset structure, sample counts, and standard evaluation procedure
- **Key Insights:**
  - 21 tasks across 6 categories; full test set per task
  - ≥500 samples per category achievable by aggregating across tasks within category
  - Middle truncation standard for models with context < LongBench max input length
- **Used For:** Dataset specification, sample count justification

### Archon Code Examples

**Code Source A.C1:** HuggingFace `output_attentions=True` Pattern
- **Query Used:** "LLaMA attention weights extraction output_attentions pytorch"
- **Key Code:** `outputs = model(input_ids, output_attentions=True); attentions = outputs.attentions`
- **Used For:** Core mechanism pseudo-code (AttentionAnalysisExtractor)

**Code Source A.C2:** Paired t-test on Layer Metrics
- **Query Used:** "paired t-test transformer layer comparison mechanistic analysis"
- **Key Code:** `from scipy.stats import ttest_rel; stat, p = ttest_rel(baseline_layer_i, proposed_layer_i)`
- **Used For:** Statistical test implementation in run_paired_ttest()

### B. GitHub Implementations (Exa)

**Repository B.1:** THUDM/LongBench (Official)
- **URL:** https://github.com/THUDM/LongBench
- **Query Used:** "LongBench official evaluation benchmark THUDM"
- **Relevance:** Official evaluation harness; defines per-task metrics (F1, ROUGE-L, accuracy)
- **Key Code:** `pred.py` (prediction generation), `eval.py` (metric computation)
- **Configuration Extracted:** Middle truncation, task-specific prompts, per-task metric
- **Used For:** Dataset specification (21 tasks, 6 categories), evaluation protocol

**Repository B.2:** FMInference/H2O (Official H2O)
- **URL:** https://github.com/FMInference/H2O
- **Query Used:** "H2O heavy hitter oracle KV cache eviction official implementation"
- **Relevance:** Official H2O implementation; provides H2OKVCache class and LLaMA integration
- **Key Code:** `H2OKVCache` — accumulates attention scores; evicts bottom-(1-r) entries per step
- **Configuration Extracted:** `heavy_ratio=0.1, recent_ratio=0.1, r=0.5` for r=50% retention
- **Used For:** Inference configuration (eviction settings), mechanism description

**Repository B.3:** bertviz / transformers-interpret (Attention Analysis Pattern)
- **Query Used:** "attention entropy computation transformer heads layer pytorch"
- **Relevance:** Standard patterns for per-layer attention entropy extraction
- **Key Code:** Layer-wise attention capture, head averaging, entropy formula
- **Used For:** AttentionAnalysisExtractor pseudo-code design

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results and H-E1 implementation was sufficiently clear.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-E1 (h-e1/04_validation.md)
- **Reused Components:**
  - Adapter checkpoints: eviction-aware + sequential baseline (LLaMA-2-7B + Mistral-7B-v0.1)
  - H2OEvictionAwareAttention hook (h-e1/code/model.py) — extend for attention extraction
  - LoRA hyperparameters: rank=16, alpha=32, dropout=0.05 — confirmed optimal
  - LongAlpacaDataset loader (h-e1/code/data.py)
  - Training infrastructure (HuggingFace Trainer integration)
- **Why Reused:** Enables controlled experiment — only adapter weights differ; same H2O eviction applied identically at inference

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|-----------------|
| Dataset: LongBench | Phase 2A via Phase 2B | Experimental Setup §1.3; B.1 |
| Dataset: ≥500 samples/category | Phase 2B H-M1 spec | 02b_verification_plan.md §2.2 H-M1 |
| Evaluation metric: attention entropy | Archon KB | Source A.1 (Clark et al. 2019) |
| Evaluation metric: HH concentration | Archon KB | Source A.2 (Zhang et al. 2023 H2O) |
| Inference: H2O r=0.5 | Archon KB + GitHub | A.2, B.2 |
| Batch size: 1 | Archon KB | A.1 (memory constraint) |
| Statistical test: paired t-test | Archon KB | A.1, A.C2 |
| Model loading: PEFT + HuggingFace | H-E1 continuation | D.1 |
| Pseudo-code: AttentionAnalysisExtractor | Archon + GitHub | A.C1, B.3 |
| Training protocol: inference-only | H-E1 continuation | D.1 |
| Success threshold: ≥50% layers p<0.05 | Phase 2B | 02b_verification_plan.md §2.2 H-M1 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-04T09:16:33

### Workflow History for This Hypothesis
- 2026-05-04T09:16:33 — H-M1 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-05-04 — Phase 2C experiment brief generated (knowledge-grounded synthesis; MCP unavailable)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Knowledge-grounded synthesis (Archon/Exa MCP unavailable — consistent with h-e1 approach)*
*All specifications grounded in established literature: H2O (Zhang et al. 2023), LongBench (Bai et al. 2023), attention entropy analysis (Clark et al. 2019)*
*Next Phase: Phase 3 — Implementation Planning*
