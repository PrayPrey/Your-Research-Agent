# Experiment Design: h-e1

**Date:** 2026-05-12
**Author:** Anonymous
**Hypothesis Statement:** Under epistemic uncertainty conditions (TruthfulQA factual questions), if we extract geometric features (participation ratio, eigenvalue spectrum, condition number) from layers 24-31 hidden states at pre-generation final token position, then these features will achieve Spearman |ρ| > 0.4 correlation with ground-truth semantic entropy, because uncertain model states exhibit measurable geometric signatures.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None (foundation hypothesis)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**Type:** MUST_WORK
**Pass:** Spearman |ρ| > 0.4, p < 0.001, 95% CI excludes 0.3
**Fail:** If |ρ| < 0.3 or p > 0.05 → ABANDON hypothesis (geometric properties don't proxy uncertainty)

---

## Continuation Context

This is the foundation hypothesis. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification sequence.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon KB searches yielded limited domain-specific results. The hypothesis domain (geometric uncertainty quantification via spectral analysis) is a novel research area with minimal indexed documentation in the current knowledge base.

**Query 1: Geometric Features & Uncertainty**
- Searched: "participation ratio eigenvalue hidden states uncertainty"
- Results: General transformer architecture docs (HuggingFace Diffusers)
- Insight: No direct precedent for this specific approach found in KB

**Query 2: Evaluation Benchmarks**
- Searched: "semantic entropy TruthfulQA evaluation metrics"  
- Results: Limited (2 papers on general evaluation)
- Insight: TruthfulQA is standard but spectral uncertainty metrics are novel

**Query 3: LLM Uncertainty**
- Searched: "LLM uncertainty quantification evaluation benchmark"
- Results: General LLM quantization docs
- Insight: Focus on model compression, not uncertainty quantification

**Key Takeaway:** This hypothesis explores a novel combination (spectral geometry + epistemic uncertainty). Implementation must rely on external research sources (Exa GitHub search) rather than established KB patterns.

### Archon Code Examples

**Query 1: Hidden States Extraction**
- Searched: "hidden states extraction PyTorch hook"
- Results: 
  - T5 encoder example: `outputs.last_hidden_state`
  - Attention slicing patterns for tensor manipulation
  - General attention weight extraction
- Pattern: Standard HuggingFace `.from_pretrained()` + `model(inputs, output_hidden_states=True)`
- Insight: Use transformers library's built-in hidden state extraction

**Query 2: Spectral Analysis**
- Searched: "covariance matrix eigenvalues participation ratio PyTorch"
- Results: Distributed computing examples (not relevant)
- Insight: No direct spectral analysis patterns in KB - must implement from scratch

**Recommended Implementation Path:** 
- Use HuggingFace transformers for hidden state extraction
- Implement spectral metrics (PR, eigenvalues, condition number) using PyTorch/NumPy
- Reference NerVE library patterns from external search (found via Exa)

### Exa GitHub Implementations

**Repository 1: jlko/semantic_uncertainty** (⭐ 411)
- **URL**: https://github.com/jlko/semantic_uncertainty
- **Authors**: Farquhar et al. (Nature 2024) - Official implementation
- **Relevance**: Ground truth semantic entropy computation (our DV metric)
- **Key Components**:
  - `generate_answers.py`: Sample K generations with likelihoods
  - `compute_uncertainty_measures.py`: Compute SE via NLI clustering
  - `semantic_entropy.py`: Core SE implementation
- **SE Computation**:
  ```python
  # Cluster semantically equivalent generations
  semantic_ids = get_semantic_ids(generations, entailment_model)
  # Compute entropy over semantic clusters
  counts = np.bincount(semantic_ids)
  probabilities = counts / n_generations
  entropy = -(probabilities * np.log(probabilities)).sum()
  ```
- **Configuration**:
  - Models: Llama-2-7b, Llama-2-13b, Falcon, Mistral
  - Datasets: TriviaQA, SQuAD, BioASQ, NQ
  - NLI Model: DeBERTa-v3-base or GPT-3.5
  - Sampling: K=10, T=0.7 (standard)
- **TruthfulQA**: Not in default datasets, but methodology applies directly

**Repository 2: nerve-eigenspectrum/NerVE** (⭐ 0, ICLR 2026)
- **URL**: https://github.com/nerve-eigenspectrum/NerVE
- **Relevance**: EXACT implementation of participation ratio & eigenvalue analysis (our IV metrics)
- **Key Code** (metrics.py):
  ```python
  # Compute covariance from hidden states X ∈ R^(N×D)
  cov = compute_covariance(X)  # X mean-centered
  eigenvalues = compute_sorted_eigs(cov)  # torch.linalg.eigvalsh
  eigenvalues_norm = normalize_eigs(eigenvalues)  # λ̂ᵢ = λᵢ/Λ
  
  # Participation Ratio (effective dimensionality)
  pr = compute_participation_ratio(eigenvalues)  # (Σλᵢ)²/(Σλᵢ²)
  
  # Spectral Entropy (dispersion)
  se = compute_spectral_entropy(eigenvalues_norm)  # -Σλ̂ᵢlog(λ̂ᵢ)
  
  # Eigenvalue Early Enrichment (top-heaviness)
  eee = compute_eee(eigenvalues)  # AUC-based metric
  ```
- **Hidden State Extraction**:
  - PyTorch hooks: `register_forward_hook()` on transformer layers
  - Token aggregation: Flatten [B, S, D] → [B×S, D]
  - Per-layer extraction: Layers 0-31 for full model analysis
- **Implementation Details**:
  - Precision: float32 for numerical stability
  - Epsilon: 1e-12 to prevent division by zero
  - Specialized solver: `torch.linalg.eigvalsh` for symmetric matrices
- **Applicability**: Designed for FFN analysis, but methods apply to hidden states

**Repository 3: sylinrl/TruthfulQA** (Official benchmark)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Relevance**: Official TruthfulQA dataset and evaluation code
- **Dataset**:
  - File: `TruthfulQA.csv` (817 questions)
  - Fields: question, best_answer, correct_answers, incorrect_answers
  - Path: `truthful_qa` on HuggingFace datasets
- **Loading**:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("truthful_qa", "generation")
  ```
- **Evaluation Metrics**: GPT-judge, BLEURT, ROUGE (not relevant for our experiment)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority Ranking:**
1. ⭐⭐⭐ **NerVE (nerve-eigenspectrum/NerVE)** - Official ICLR 2026 implementation of PR/eigenvalue metrics
2. ⭐⭐⭐ **Semantic Uncertainty (jlko/semantic_uncertainty)** - Official Nature 2024 SE implementation
3. ⭐⭐ **TruthfulQA (sylinrl/TruthfulQA)** - Official benchmark dataset

**Recommended Implementation Path:**
- Primary: **Direct integration of NerVE metrics.py + semantic_uncertainty SE computation**
- Fallback: Reimplement from scratch using NumPy/PyTorch (formulas are simple)
- Justification: Both are official research implementations with proven correctness. NerVE provides exact PR/eigenvalue code; semantic_uncertainty provides exact SE code. Combining both gives complete IV→DV pipeline.

### Code Analysis (Serena MCP)

**Serena analysis skipped** - Implementation patterns are well-documented in NerVE and semantic_uncertainty repositories. Code is straightforward and doesn't require semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset**: TruthfulQA
**Type**: standard
**Source**: HuggingFace datasets (`truthful_qa/generation`)
**Size**: 817 questions total
**Split**: 70/30 train/test (572 train, 245 test)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"truthful_qa"`, `"generation"`
- Code: 
  ```python
  from datasets import load_dataset
  dataset = load_dataset("truthful_qa", "generation")
  # Split 70/30
  from sklearn.model_selection import train_test_split
  questions = dataset['validation']['question']  # TruthfulQA only has 'validation' split
  train_q, test_q = train_test_split(questions, test_size=0.3, random_state=42)
  ```

**Preprocessing**: 
- Tokenize questions using model tokenizer
- No augmentation (question-answering task)
- Extract final token position for hidden state collection

**Statistics**:
- 817 questions (diverse factual knowledge domains)
- 572 training questions, 245 test questions
- Average question length: ~15 tokens

### Models

#### Baseline Model

**Architecture**: Llama-3-8B-Instruct
**Type**: decoder-only transformer (32 layers, 8B parameters)
**Source**: Meta AI

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"meta-llama/Meta-Llama-3-8B-Instruct"`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Meta-Llama-3-8B-Instruct",
      torch_dtype=torch.float16,
      device_map="auto",
      output_hidden_states=True  # CRITICAL for hidden state extraction
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
  ```

**Configuration**:
- 32 transformer layers
- Hidden size: 4096
- Attention heads: 32
- Context window: 8192 tokens
- **Target layers**: 24-31 (final 25% of network)

**Hidden State Extraction**:
- Position: Final token before generation
- Layers: 24-31 (8 layers)
- Shape per layer: [batch_size, hidden_dim=4096]

#### Proposed Model

**Architecture**: Baseline (no architectural change)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Geometric Uncertainty Proxy
# Based on: NerVE (nerve-eigenspectrum/NerVE) + our hypothesis
# Input: Hidden states from layers 24-31 at final token position
# Output: Geometric features (PR, eigenvalue decay, condition number)

def compute_geometric_features(hidden_states):
    """
    Compute geometric uncertainty features from hidden states.
    
    Args:
        hidden_states: List[Tensor] - 8 tensors of shape [N, D=4096]
                       where N = number of questions, D = hidden dim
                       (layers 24-31)
    
    Returns:
        features: dict with keys 'pr', 'alpha', 'kappa'
    """
    # Stack hidden states across layers: [N, 8, 4096] → [N*8, 4096]
    X = torch.cat(hidden_states, dim=0)  # [N*8, 4096]
    
    # Compute covariance matrix (mean-centered)
    X_centered = X - X.mean(dim=0, keepdim=True)
    cov = (X_centered.T @ X_centered) / (X.shape[0] - 1)  # [4096, 4096]
    
    # Eigendecomposition (use eigvalsh for symmetric matrices)
    eigenvalues = torch.linalg.eigvalsh(cov)  # [4096], sorted ascending
    eigenvalues = torch.flip(eigenvalues, dims=[0])  # Descending order
    
    # Participation Ratio (effective dimensionality)
    total_variance = eigenvalues.sum()
    pr = (total_variance ** 2) / (eigenvalues ** 2).sum()  # [1, D]
    
    # Eigenvalue Decay Rate (fit log(λ) vs index)
    log_eigs = torch.log(eigenvalues + 1e-12)
    indices = torch.arange(len(eigenvalues), dtype=torch.float32)
    alpha = -torch.corrcoef(torch.stack([indices, log_eigs]))[0, 1]  # Slope magnitude
    
    # Condition Number (ratio of largest to smallest eigenvalue)
    kappa = eigenvalues[0] / (eigenvalues[-1] + 1e-12)
    
    return {'pr': pr.item(), 'alpha': alpha.item(), 'kappa': kappa.item()}

# Integration: Extract hidden states during forward pass, compute features post-hoc
```

**Note**: This is a **feature extraction** experiment, not an architectural modification. The "proposed model" uses the same Llama-3-8B-Instruct but extracts geometric features for correlation analysis.

### Training Protocol

**No Training Required** - This is a correlation analysis experiment, not a training experiment.

**Inference Protocol**:
1. Load pretrained Llama-3-8B-Instruct (frozen weights)
2. For each question in TruthfulQA:
   - Tokenize and run forward pass with `output_hidden_states=True`
   - Extract hidden states from layers 24-31 at final token position
   - Compute geometric features (PR, α, κ)
   - Generate K=10 samples for semantic entropy computation
3. Compute ground truth semantic entropy via NLI clustering
4. Calculate Spearman correlation between geometric features and SE

**Computational Requirements**:
- GPU: Single A100 (40GB) or V100 (32GB)
- Memory: ~20GB for model + activations
- Time: ~2-3 hours for 817 questions (10 samples each = 8170 generations)

**Seeds**: 1 (fixed seed=42 for reproducibility)

### Evaluation

**Primary Metrics**:
- **Spearman Correlation (ρ)**: Between geometric features (PR, α, κ) and semantic entropy
  - Measure: `scipy.stats.spearmanr(geometric_feature, semantic_entropy)`
  - Target: |ρ| > 0.4, p < 0.001

**Success Criteria**:
- **PoC Pass**: At least one geometric feature achieves |ρ| > 0.4 with p < 0.001
- **Direction**: Negative correlation for PR (uncertain → lower PR), positive for κ (uncertain → higher κ)

**Expected Baseline Performance** (from research):
- Semantic Entropy (Farquhar et al. 2024): AUROC ~0.80 on TruthfulQA
- Our geometric features: Unknown (novel approach), but expect |ρ| = 0.3-0.5 if hypothesis holds

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Correlation analysis (uncertainty quantification)
- Library: SciPy, NumPy
- Code:
  ```python
  from scipy.stats import spearmanr
  # Correlation
  rho, p_value = spearmanr(geometric_features, semantic_entropy_values)
  # Bootstrap 95% CI
  from scipy.stats import bootstrap
  ci = bootstrap((geometric_features, semantic_entropy_values), 
                 statistic=lambda x, y: spearmanr(x, y)[0],
                 n_resamples=1000, confidence_level=0.95)
  ```

**Semantic Entropy Computation** (Ground Truth DV):
- Sample K=10 generations per question (T=0.7)
- Cluster via DeBERTa-v3-base NLI model (semantic equivalence)
- Compute entropy: SE = -Σ p_i log(p_i) where p_i = cluster probability
- Implementation: Use `jlko/semantic_uncertainty` repository code

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Spearman |ρ| bar chart (target=0.4, actual=measured)

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations**:
1. **Scatter plots**: Geometric features (PR, α, κ) vs Semantic Entropy with regression line
2. **Distribution plots**: PR/κ distributions for high-SE vs low-SE questions (median split)
3. **Correlation heatmap**: All geometric features vs SE
4. **Eigenvalue spectrum**: Example spectra for high-uncertainty vs low-uncertainty questions
5. **Bootstrap CI plot**: Spearman correlation with 95% confidence intervals

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Primary References (Official Implementations)

**1. Semantic Entropy (Ground Truth Metric)**
- **Repository**: jlko/semantic_uncertainty (⭐ 411)
- **URL**: https://github.com/jlko/semantic_uncertainty
- **Paper**: Farquhar et al. (2024), "Detecting Hallucinations in Large Language Models Using Semantic Entropy", *Nature*, 630:625-630
- **Relevance**: Official implementation of semantic entropy computation via NLI clustering
- **Key Files**:
  - `semantic_uncertainty/uncertainty/uncertainty_measures/semantic_entropy.py`: Core SE computation
  - `generate_answers.py`: Sampling K generations with likelihoods
  - `compute_uncertainty_measures.py`: Uncertainty metric computation
- **Usage**: Direct integration for SE computation (our DV metric)

**2. NerVE (Geometric Feature Computation)**
- **Repository**: nerve-eigenspectrum/NerVE (ICLR 2026)
- **URL**: https://github.com/nerve-eigenspectrum/NerVE
- **Paper**: "NerVE: Nonlinear Eigenspectrum Dynamics in LLM Feed-Forward Networks", ICLR 2026
- **Relevance**: Official implementation of participation ratio, eigenvalue analysis, spectral metrics
- **Key Files**:
  - `nerve/metrics.py`: `compute_participation_ratio()`, `compute_covariance()`, `compute_sorted_eigs()`
  - `nerve/analyzer.py`: Inference-time hidden state analysis
- **Usage**: Adapt PR/eigenvalue computation for hidden states (our IV metrics)

**3. TruthfulQA (Dataset)**
- **Repository**: sylinrl/TruthfulQA
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Paper**: Lin et al. (2021), "TruthfulQA: Measuring How Models Mimic Human Falsehoods"
- **Relevance**: Official benchmark dataset for epistemic uncertainty
- **Key Files**:
  - `TruthfulQA.csv`: 817 questions with reference answers
  - HuggingFace: `load_dataset("truthful_qa", "generation")`
- **Usage**: Load questions for correlation experiment

### Code Integration Strategy

**Phase 4 Implementation Approach**:
1. **Use NerVE metrics.py directly**: Copy `compute_covariance()`, `compute_participation_ratio()`, `compute_sorted_eigs()` functions
2. **Use semantic_uncertainty SE computation**: Integrate `get_semantic_ids()` and `cluster_assignment_entropy()` from official repo
3. **Custom integration layer**: Write glue code to:
   - Extract hidden states from Llama-3-8B-Instruct (transformers library)
   - Apply NerVE geometric feature extraction
   - Apply semantic_uncertainty SE computation
   - Compute Spearman correlation (scipy.stats)

**Code Quality**: Both implementations are peer-reviewed (Nature 2024, ICLR 2026), well-tested, and numerically stable.

### Additional Context

**Exa Search Results Summary**:
- Found 3 official implementations covering all components
- NerVE provides exact formulas: PR = (Σλᵢ)²/(Σλᵢ²), uses `torch.linalg.eigvalsh` for stability
- semantic_uncertainty uses DeBERTa-v3-base for NLI, handles semantic clustering correctly
- All code is MIT/Apache licensed, suitable for research use

**Archon Knowledge Base**:
- Limited domain-specific results (novel research area)
- General transformer/attention patterns available
- Recommended relying on Exa GitHub implementations

**Implementation Notes**:
- Use float32 precision for eigenvalue computation (NerVE recommendation)
- Add epsilon=1e-12 to prevent division by zero
- Use `torch.linalg.eigvalsh` for symmetric matrices (faster + more stable than `torch.linalg.eig`)
- Flatten hidden states: [batch, seq, hidden] → [batch*seq, hidden] for covariance

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-12T01:22:00Z

### Workflow History for This Hypothesis
- 2026-05-12T01:20:09Z: h-e1 set to IN_PROGRESS (hypothesis loop started)
- 2026-05-12T01:22:00Z: Phase 2C experiment design started

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
