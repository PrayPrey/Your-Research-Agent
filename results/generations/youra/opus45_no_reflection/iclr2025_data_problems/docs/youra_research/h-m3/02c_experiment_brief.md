# Experiment Design: H-M3

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Attribution approximation methods make different assumptions about curvature (EK-FAC: Kronecker, TracIn: gradient-only, TRAK: random projection)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing approximation assumption sensitivity across architectures.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 PASSED with 90.93% curvature difference)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (Hessian Curvature Divergence - PASSED)

### Gate Condition
EK-FAC approximation error should be lower on GPT-2 than BERT (Kronecker assumption fits causal structure). TracIn gradient signal should be stronger on BERT (benefits from dense gradients). TRAK should show minimal architecture variance (random projection invariant).

**Success Threshold:** >10% relative difference in approximation quality metrics between architectures for at least one method.

---

## Continuation Context

H-M2 validated that GPT-2 exhibits 11x higher top Hessian eigenvalue (0.502) compared to BERT (0.046). This curvature difference should affect how well each attribution method's mathematical assumptions hold:

1. **EK-FAC** assumes Kronecker-factored curvature (G ≈ A ⊗ B). Causal attention's block structure may better satisfy this.
2. **TracIn** uses first-order gradient dot products only. Dense bidirectional gradients in BERT may provide stronger signal.
3. **TRAK** uses random Johnson-Lindenstrauss projections. Theory predicts architecture invariance.

### Previous Hypothesis Results
- H-M1: Attention pattern divergence confirmed (BERT bidirectional O(n²), GPT-2 causal O(n²/2))
- H-M2: Hessian curvature divergence confirmed (90.93% difference in top eigenvalue)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches. General curvature approximation and attention mechanisms documented.

### Archon Code Examples

PyTorch scaled dot-product attention with causal masking patterns found. Relevant for understanding gradient flow differences.

### Exa GitHub Implementations

**Primary Implementation Sources:**

1. **kronfluence** (github.com/pomonam/kronfluence)
   - EK-FAC influence functions for transformers
   - Supports `nn.Linear`, `nn.Conv2d` modules
   - Strategies: `identity`, `diagonal`, `kfac`, `ekfac`
   - API: `Analyzer.fit_all_factors()`, `compute_pairwise_scores()`

2. **TRAK** (github.com/MadryLab/trak)
   - Random projection-based attribution
   - Custom CUDA kernel for JL projection
   - API: `TRAKer.featurize()`, `score()`, `finalize_scores()`
   - Default projection dim: 2048

3. **TracIn** (multiple implementations)
   - rollovd/TracIn-PyTorch: Batch processing support
   - captum.influence: TracInCPFast for last-layer optimization
   - Formula: `TracInCP(z,z') = Σ ηᵢ∇ℓ(wₜᵢ,z)·∇ℓ(wₜᵢ,z')`

4. **simple-influence** (github.com/pomonam/simple-influence)
   - Unified interface: `InfluenceFunctionComputer`, `TracinComputer`, `TrakComputer`
   - Same `compute_scores_with_loader()` API across methods

### 🎯 Implementation Priority Assessment

**CRITICAL: Use established libraries for fair comparison**

**Recommended Implementation Path:**
- Primary: kronfluence (EK-FAC), traker (TRAK), simple-influence (TracIn wrapper)
- Fallback: Custom TracIn using gradient checkpoints
- Justification: Published libraries ensure implementation quality equivalence (Assumption A4)

### Code Analysis (Serena MCP)

Not required - using external libraries, no local codebase analysis needed.

---

## Experiment Specification

### Dataset

**Name:** SST-2 (Stanford Sentiment Treebank v2)
**Source:** GLUE benchmark via HuggingFace datasets
**Type:** standard

| Split | Samples | Usage |
|-------|---------|-------|
| Train | 67,349 | Attribution source |
| Validation | 872 | Query examples |
| Mislabeled | 5% of train (~3,367) | Detection target |

**Preprocessing:**
- Tokenization: Model-specific tokenizer (BERT: bert-base-uncased, GPT-2: gpt2)
- Max sequence length: 128 tokens
- Padding: Right-side, to max_length

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: glue/sst2
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("glue", "sst2")
train_data = dataset["train"]
val_data = dataset["validation"]
```

### Models

#### Baseline Model

| Model | Parameters | Layers | Architecture |
|-------|------------|--------|--------------|
| BERT-base-uncased | 110M | 12 | Encoder-only |
| GPT-2 | 124M | 12 | Decoder-only |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: bert-base-uncased, gpt2
- Code:
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# BERT
bert_model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=2
)
bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# GPT-2 (with classification head)
gpt2_model = AutoModelForSequenceClassification.from_pretrained(
    "gpt2", num_labels=2
)
gpt2_model.config.pad_token_id = gpt2_model.config.eos_token_id
gpt2_tokenizer = AutoTokenizer.from_pretrained("gpt2")
gpt2_tokenizer.pad_token = gpt2_tokenizer.eos_token
```

#### Proposed Model

**Architecture:** Same as baseline - comparison is across attribution methods, not model modifications.

**Core Mechanism Implementation:**

```python
# Approximation Quality Measurement Pseudo-code

def measure_ekfac_approximation_quality(model, dataset, n_samples=1000):
    """
    Measure how well EK-FAC Kronecker assumption holds.
    Lower reconstruction error = better fit.
    """
    from kronfluence.analyzer import Analyzer, prepare_model
    
    # Fit EK-FAC factors
    analyzer = Analyzer(model=prepare_model(model, task), task=task)
    analyzer.fit_all_factors(factors_name="ekfac", dataset=dataset)
    
    # Compute influence scores
    scores_ekfac = analyzer.compute_pairwise_scores(
        query_dataset=query_set, train_dataset=dataset,
        factors_name="ekfac"
    )
    
    # Compare to ground truth (if available) or self-consistency
    return compute_reconstruction_metrics(scores_ekfac)

def measure_tracin_gradient_signal(model, checkpoints, dataset):
    """
    Measure TracIn gradient dot-product magnitude.
    Higher magnitude = stronger signal.
    """
    scores = []
    for ckpt in checkpoints:
        model.load_state_dict(torch.load(ckpt))
        for query in query_set:
            for train_sample in dataset:
                grad_query = compute_gradient(model, query)
                grad_train = compute_gradient(model, train_sample)
                score = torch.dot(grad_query.flatten(), grad_train.flatten())
                scores.append(score.abs().item())
    return {
        "mean_signal": np.mean(scores),
        "std_signal": np.std(scores),
        "snr": np.mean(scores) / np.std(scores)  # signal-to-noise
    }

def measure_trak_projection_variance(model, dataset, proj_dims=[1024, 2048, 4096]):
    """
    Measure TRAK score variance across different projection seeds.
    Lower variance = more stable (architecture-invariant).
    """
    from trak import TRAKer
    
    variances = []
    for seed in [0, 1, 2, 3, 4]:
        traker = TRAKer(model=model, task='text_classification',
                       train_set_size=len(dataset), proj_dim=2048, seed=seed)
        # ... compute scores
        scores = traker.finalize_scores()
        variances.append(scores)
    
    return {
        "score_variance": np.var(np.stack(variances), axis=0).mean(),
        "rank_correlation": compute_avg_spearman(variances)
    }

def compare_approximation_quality(bert_model, gpt2_model, dataset):
    """
    Main comparison: measure approximation quality for each method on each arch.
    """
    results = {}
    
    for arch_name, model in [("BERT", bert_model), ("GPT-2", gpt2_model)]:
        results[arch_name] = {
            "ekfac": measure_ekfac_approximation_quality(model, dataset),
            "tracin": measure_tracin_gradient_signal(model, checkpoints, dataset),
            "trak": measure_trak_projection_variance(model, dataset)
        }
    
    # Compute relative differences
    for method in ["ekfac", "tracin", "trak"]:
        bert_metric = results["BERT"][method]["primary_metric"]
        gpt2_metric = results["GPT-2"][method]["primary_metric"]
        diff = abs(bert_metric - gpt2_metric) / max(bert_metric, gpt2_metric)
        results[f"{method}_arch_diff"] = diff
    
    return results
```

### Training Protocol

**Fine-tuning (both models):**
- Optimizer: AdamW
- Learning rate: 2e-5
- Schedule: Linear warmup (10% steps) + linear decay
- Batch size: 32
- Epochs: 3
- Checkpoints: Save at epoch 1, 2, 3 (for TracIn)
- Loss: CrossEntropyLoss
- Gradient clipping: 1.0

**Mislabeled Injection:**
- Randomly flip 5% of training labels
- Record mislabeled indices as ground truth

### Evaluation

**Primary Metrics:**

| Method | Metric | Interpretation |
|--------|--------|----------------|
| EK-FAC | Mislabeled detection AUC | Higher = better approximation |
| EK-FAC | Kronecker reconstruction error | Lower = better Kronecker fit |
| TracIn | Gradient signal magnitude | Higher = stronger signal |
| TracIn | Mislabeled detection AUC | Higher = better |
| TRAK | Cross-seed rank correlation | Higher = more stable |
| TRAK | Mislabeled detection AUC | Higher = better |

**Gate Metric:**
- Relative difference in mislabeled detection AUC across architectures per method
- EK-FAC: expect GPT-2 > BERT (better Kronecker fit)
- TracIn: expect BERT > GPT-2 (denser gradients)
- TRAK: expect |diff| < 5% (architecture invariant)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (mislabeled detection)
- Library: scikit-learn
- Code:
```python
from sklearn.metrics import roc_auc_score, average_precision_score

def compute_mislabeled_auc(influence_scores, mislabeled_indices):
    # Higher influence = more likely mislabeled
    labels = np.zeros(len(influence_scores))
    labels[mislabeled_indices] = 1
    return roc_auc_score(labels, influence_scores)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mislabeled detection AUC for each method × architecture combination (6 bars total)

#### Additional Figures (LLM Autonomous)

1. **Approximation Quality Heatmap**: Methods (rows) × Architectures (cols) with quality scores
2. **Score Distribution Comparison**: Violin plots of influence score distributions per method/arch
3. **Rank Correlation Matrix**: Spearman correlation between method rankings on same queries

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on both architectures
2. At least one method shows >10% AUC difference across architectures
3. EK-FAC shows better performance on GPT-2 than BERT (as predicted)
4. TracIn shows comparable or better performance on BERT than GPT-2
5. TRAK shows <5% difference across architectures (invariance)

---

## Appendix: Reference Implementations

| Library | Method | Paper | Installation |
|---------|--------|-------|--------------|
| kronfluence | EK-FAC | Grosse et al. 2023 | `pip install kronfluence` |
| traker | TRAK | Park et al. 2023 | `pip install traker[fast]` |
| simple-influence | TracIn wrapper | Bae et al. 2024 | `pip install -e git+github.com/pomonam/simple-influence` |
| captum | TracInCP | Pruthi et al. 2020 | `pip install captum` |

**Key Papers:**
1. Grosse et al. (2023) - "Studying Large Language Model Generalization with Influence Functions" - EK-FAC for LLMs
2. Park et al. (2023) - "TRAK: Attributing Model Behavior at Scale" - ICML, random projection method
3. Pruthi et al. (2020) - "Estimating Training Data Influence by Tracing Gradient Descent" - NeurIPS, TracIn

**GitHub Repositories:**
- https://github.com/pomonam/kronfluence (EK-FAC, primary)
- https://github.com/MadryLab/trak (TRAK, primary)
- https://github.com/pomonam/simple-influence (unified interface)
- https://github.com/pytorch/captum (TracInCP)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- H-M2 PASSED: Hessian curvature divergence confirmed (90.93% diff)
- H-M1 PASSED: Attention pattern divergence confirmed
- H-E1 PASSED: Architecture-method interaction exists

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
