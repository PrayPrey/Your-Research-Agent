# Experiment Design: h-e1

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Under selective prediction on TruthfulQA (817 human-annotated questions) using Llama-3.1-8B-Instruct, if we apply any single-pass UQ method (temperature scaling, conformal prediction, or MC dropout k≤10), then at least one method achieves AUROC ≥ 0.70, because effective uncertainty quantification enables abstention from incorrect predictions.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C active)
**Prerequisites Satisfied:** None (foundation hypothesis)
**Gate Status:** MUST_WORK (blocking - if fails, stop entire verification)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** Existence
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK: If max(AUROC across 6 methods) < 0.70, STOP experiment and document 8B scale limitation. Recommend ≥70B model follow-up.

---

## Continuation Context

*None* - This is the foundation hypothesis (H-E1). No previous hypotheses executed yet.

### Previous Hypothesis Results (if applicable)
*N/A* - First hypothesis in verification plan

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Selective Prediction & Uncertainty Quantification**
- No direct matches found in current Archon KB
- Search results returned diffusion model papers (UniPC, consistency models)
- Domain mismatch: KB indexed primarily for vision/generative models, not NLP uncertainty

**Query 2: Temperature Scaling & Conformal Prediction**
- Limited relevance: Found calibration code for quantization (optimum-quanto)
- No temperature scaling for LLM calibration found
- No conformal prediction implementations found

**Query 3: TruthfulQA Benchmark**
- No indexed papers or implementations for TruthfulQA evaluation
- KB lacks NLP evaluation benchmark implementations

**Key Finding:** Archon KB does not contain relevant UQ/selective prediction content for LLMs. Implementation research will rely on Exa GitHub search (Step 03) and manual specification.

### Archon Code Examples

**Query 1: MC Dropout Implementation**
- No MC dropout code found (search returned diffusion attention mechanisms)
- No Bayesian uncertainty code for LLMs found

**Query 2: Temperature Scaling & Calibration**
- Found model calibration code (optimum-quanto) but for quantization, not temperature scaling
- No post-hoc calibration examples for classification/QA tasks

**Gap Identified:** Archon lacks code examples for UQ methods. Will use standard PyTorch patterns + Exa search for validation.

### Exa GitHub Implementations

**Query 1: TruthfulQA + UQ + Selective Prediction**

**Repository 1: sylinrl/TruthfulQA** (⭐911 - Official)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Relevance**: OFFICIAL TruthfulQA benchmark implementation (author: Stephanie Lin)
- **Dataset**: TruthfulQA.csv (817 questions, human-annotated truthfulness labels)
- **Evaluation Metrics**: GPT-judge, BLEURT, ROUGE, BLEU, MC1/MC2 tasks
- **Key Insight**: Standard evaluation protocol uses `evaluate.py` with preset prompts

**Repository 2: insomniac-asif/honest-confidence** (Selective Prediction on TruthfulQA)
- **URL**: https://github.com/insomniac-asif/honest-confidence
- **Relevance**: Selective prediction with calibration layer for TruthfulQA (AUROC, ECE, abstention)
- **Key Results**: ECE 0.479 → 0.139 (3.4× improvement), AUROC 0.577 (raw) vs 0.509 (calibrated)
- **Architecture**: Deterministic honesty layer with confidence capping
- **Metrics**: ECE, AUROC, abstention rate, accuracy-on-answered, confident-falsehood rate

**Repository 3: mbzuai-nlp/llm-tad-uncertainty** (EMNLP 2025)
- **URL**: https://github.com/mbzuai-nlp/llm-tad-uncertainty
- **Relevance**: Trainable Attention-Based Dependency (TAD) for LLM UQ (100× faster than MC)
- **Models Tested**: LLaMA-3.1, Gemma-2, Qwen-2.5
- **Method**: Supervised UQ from attention maps + token probs (recurrent uncertainty)
- **Note**: Requires training, not single-pass (outside our scope)

**Query 2: Temperature Scaling + Conformal Prediction + MC Dropout**

**Repository 4: mc-dropout-pytorch (PyPI Package)**
- **URL**: https://pypi.org/project/mc-dropout-pytorch/
- **Relevance**: Clean MC Dropout implementation (Gal & Ghahramani 2016)
- **Key Code**:
  ```python
  from mc_dropout_pytorch import BayesianMLP, MCDropoutInference
  model = BayesianMLP(dropout_rate=0.1)
  mc = MCDropoutInference(model, num_samples=50, task='classification')
  out = mc(x)
  out.mean, out.variance, out.samples
  ```
- **Features**: Predictive entropy, mutual information for active learning

**Repository 5: A-SHOJAEI/adversarial-uncertainty-calibration-for-medical-diagnosis**
- **URL**: https://github.com/A-SHOJAEI/adversarial-uncertainty-calibration-for-medical-diagnosis
- **Relevance**: Combines temperature scaling + MC dropout in unified framework
- **Architecture**: Dual-head (task + adversarial calibration), ResNet-50 backbone
- **Training**: Calibration-aware loss (ECE minimization), dropout + temp scaling
- **Key Insight**: Temperature scaling applied POST-HOC, not during training

**Repository 6: ShahnawazKakarh/retinal-selective-prediction**
- **URL**: https://github.com/ShahnawazKakarh/retinal-selective-prediction
- **Relevance**: Benchmarks all 3 UQ methods (temp scaling, MC dropout, conformal) on classification
- **Key Results**:
  - Temp Scaling (T=2.25): ECE 0.146 → 0.055 (62% reduction), 1-param fit
  - MC Dropout (T=30): Best AURC, mutual information for selective prediction
  - Conformal (split, α=0.10): 90.2% coverage, avg set size 1.35
- **Code Structure**: `src/uncertainty/` (one module per method), `src/selective/risk_coverage.py` (AURC)

**Repository 7: Robust Uncertainty via MC-CP (arXiv 2308.09647)**
- **Paper**: https://arxiv.org/html/2308.09647
- **Method**: Monte Carlo-Conformal Prediction (hybrid MC + CP)
- **Key Innovation**: Adaptive MC dropout (early stopping when variance converges)
- **Algorithm**: Threshold δ + patience P → stop when Var(predictions) < δ for P consecutive passes
- **Efficiency**: Saves computation vs fixed K forward passes

**Query 3: Llama-3 + TruthfulQA Evaluation**

**Repository 8: likenneth/honest_llama**
- **URL**: https://github.com/likenneth/honest_llama/blob/master/utils.py
- **Relevance**: TruthfulQA evaluation for Llama models (with interventions)
- **Key Function**: `alt_tqa_evaluate()` - runs TruthfulQA with HF models
- **Metrics**: MC1/MC2, BLEURT, ROUGE, BLEU, GPT-judge/info
- **Usage**: Supports Llama tokenizer + custom instruction prompts

**Serena Analysis Needed**: No (code patterns clear from examples)

### 🎯 Implementation Priority Assessment

**Implementation Type:** Novel combination (not paper reproduction)
**Approach:** Build from validated components

**Recommended Implementation Path:**
- Primary: Implement UQ methods from scratch using researched patterns (mc-dropout-pytorch, honest-confidence)
- Fallback: Use TorchCP library for conformal prediction if implementation complex
- Justification: No official implementation exists (novel combination of UQ methods on TruthfulQA). Standard patterns well-documented in found repositories (especially mc-dropout-pytorch PyPI package).

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Standard UQ methods well-documented in found repositories.

---

## Experiment Specification

### Dataset

**Dataset**: TruthfulQA
**Type**: standard (established benchmark)
**Size**: 817 questions (human-annotated truthfulness labels)
**Source**: sylinrl/TruthfulQA (GitHub, official)
**Format**: CSV with questions, correct_answers, incorrect_answers columns
**Task**: Generative QA (generate 1-2 sentence answer per question)

**Splits**:
- Calibration split (~327 questions, 40%): For temperature scaling + conformal prediction calibration
- Evaluation split (~490 questions, 60%): For AUROC computation (seeded split for reproducibility)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets + manual CSV
- Identifier: `truthfulqa/truthful_qa` (HF) OR download from https://github.com/sylinrl/TruthfulQA/blob/main/TruthfulQA.csv
- Code:
  ```python
  from datasets import load_dataset
  ds = load_dataset("truthfulqa/truthful_qa", "generation")
  # OR
  import pandas as pd
  df = pd.read_csv("TruthfulQA.csv")
  ```

**Preprocessing**: None (questions used as-is with preset="qa" prompt)

**Ground Truth**: Human-annotated binary labels (correct=1, incorrect=0) from `correct_answers` field

### Models

#### Baseline Model

**Architecture**: Llama-3.1-8B-Instruct
**Type**: standard (pretrained LLM, instruction-tuned)
**Source**: Meta-Llama-3.1-8B-Instruct (HuggingFace)
**Parameters**: 8B
**Task**: Generative QA (text generation)

**Configuration**:
- Max new tokens: 100 (for 1-2 sentence answers)
- Temperature: 1.0 (baseline, before temp scaling)
- Top-p: 1.0 (no nucleus sampling)
- Batch size: 8 (memory constraint)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/Llama-3.1-8B-Instruct`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-3.1-8B-Instruct",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
  ```

**Note**: Requires HuggingFace access token for gated Llama models

#### Proposed Model

**Architecture:** Llama-3.1-8B-Instruct + UQ Methods (Temperature Scaling, Conformal Prediction, MC Dropout)

**Integration Point:** Post-generation (after logits extraction, before final prediction)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Uncertainty Quantification for Selective Prediction
# Based on: mc-dropout-pytorch, honest-confidence, retinal-selective-prediction

class UncertaintyQuantifier:
    """
    Implements 3 UQ methods for selective prediction on TruthfulQA.
    Methods: Temperature Scaling, Conformal Prediction, MC Dropout (k=1,3,5,10)
    """
    def __init__(self, model, calibration_data, method="temp_scaling", k=5, alpha=0.1):
        self.model = model
        self.method = method
        self.k = k  # MC dropout passes
        self.alpha = alpha  # Conformal prediction coverage
        self.temperature = 1.0  # Fitted on calibration set
        self.conformal_threshold = None  # Fitted on calibration set
    
    def calibrate(self, calibration_data):
        """Fit temperature or conformal threshold on calibration split."""
        if self.method == "temp_scaling":
            # Fit single temperature parameter T via cross-entropy
            self.temperature = fit_temperature(self.model, calibration_data)
        elif self.method == "conformal":
            # Compute (1-alpha) quantile of nonconformity scores
            scores = [self.nonconformity_score(x, y) for x, y in calibration_data]
            self.conformal_threshold = np.quantile(scores, 1 - self.alpha)
    
    def predict_with_uncertainty(self, x):
        """
        Generate answer + uncertainty score.
        
        Returns:
            answer: str (generated text)
            uncertainty: float (higher = less confident, should abstain)
        """
        if self.method == "temp_scaling":
            logits = self.model(x)  # (vocab_size,)
            probs = softmax(logits / self.temperature)
            uncertainty = 1.0 - max(probs)  # 1 - max confidence
            answer = self.model.generate(x)
            
        elif self.method == "conformal":
            logits = self.model(x)
            probs = softmax(logits)
            nonconformity = self.nonconformity_score(x, None)
            uncertainty = nonconformity  # Higher = more uncertain
            answer = self.model.generate(x)
            
        elif self.method == "mc_dropout":
            # Enable dropout, run k forward passes
            self.model.train()  # Keep dropout active
            answers_k = [self.model.generate(x) for _ in range(self.k)]
            logits_k = [self.model(x) for _ in range(self.k)]
            
            # Variance across k predictions = epistemic uncertainty
            probs_k = [softmax(logits) for logits in logits_k]
            mean_probs = np.mean(probs_k, axis=0)
            uncertainty = -np.sum(mean_probs * np.log(mean_probs + 1e-10))  # Entropy
            answer = answers_k[0]  # Use first sample as answer
            
        return answer, uncertainty

# Integration: After model.generate(), compute uncertainty, rank by uncertainty for AUROC
```

### Training Protocol

**No Training Required** - Using pretrained Llama-3.1-8B-Instruct frozen.

**Calibration Phase** (for Temperature Scaling + Conformal Prediction):
- Dataset: TruthfulQA calibration split (327 questions, 40%)
- Method:
  - Temperature Scaling: Fit single parameter T via cross-entropy on calibration logits
  - Conformal Prediction: Compute (1-α) quantile of nonconformity scores
- Optimizer: LBFGS (for temperature scaling), None for conformal (non-parametric)
- Epochs: 50 (temperature scaling only, ~1 minute)

**Inference Configuration**:
- Generation max tokens: 100
- Temperature: 1.0 (baseline) OR fitted T (for temp scaling method)
- Top-p: 1.0
- Batch size: 8
- Seed: 42 (fixed)

**MC Dropout Variants**:
- k=1 (baseline, no dropout)
- k=3, k=5, k=10 (stochastic forward passes)
- Dropout rate: 0.1 (standard for Llama)

### Evaluation

**Primary Metric**: AUROC (Area Under ROC Curve for selective prediction)
- Task: Binary classification (correct vs incorrect answer)
- Input: Uncertainty scores (1 per question), ground truth labels (correct=0, incorrect=1)
- Computation: Rank questions by uncertainty (high = should abstain), compute AUROC
- Success Threshold: AUROC ≥ 0.70 (at least one method must achieve this)

**Secondary Metrics**:
- Spearman ρ (correlation between uncertainty and incorrectness): ρ > 0.2 (sanity check)
- Mean AUROC ± std across 3 seeds: For variance check (though PoC uses 1 seed)

**Evaluation Protocol**:
1. Generate answers for all 490 test questions using Llama-3.1-8B
2. Apply each UQ method (6 total: temp_scaling, conformal, mc_k1, mc_k3, mc_k5, mc_k10)
3. Extract uncertainty score per question per method
4. Compute AUROC using sklearn: `roc_auc_score(y_true=correctness, y_score=uncertainty)`
5. Check if max(AUROC across 6 methods) ≥ 0.70

**Ground Truth Labels**:
- Source: Human annotations in TruthfulQA.csv (correct_answers field)
- Binary: correct=0 (model should be confident), incorrect=1 (model should be uncertain)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary_classification (selective prediction)
- Library: sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import roc_auc_score
  from scipy.stats import spearmanr
  
  auroc = roc_auc_score(y_true=labels, y_score=uncertainties)
  spearman_rho, _ = spearmanr(uncertainties, incorrectness)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

**Figure 1: AUROC Comparison Across Methods** (bar chart)
- X-axis: UQ methods (temp_scaling, conformal, mc_k1, mc_k3, mc_k5, mc_k10)
- Y-axis: AUROC (0.5 to 1.0 range)
- Horizontal line: Success threshold (0.70)
- Purpose: Show which methods pass gate condition

**Figure 2: Uncertainty Distribution** (histogram, 2x3 subplots)
- One subplot per UQ method
- X-axis: Uncertainty score
- Y-axis: Frequency
- Color: Correct (blue) vs Incorrect (red) answers
- Purpose: Show separation between correct/incorrect predictions

**Figure 3: ROC Curves** (line plot)
- One curve per UQ method
- X-axis: False Positive Rate
- Y-axis: True Positive Rate
- Purpose: Visualize selective prediction trade-off

All figures saved to `{hypothesis_folder}/figures/` with filenames: `auroc_comparison.png`, `uncertainty_distributions.png`, `roc_curves.png`

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**No relevant sources found** - Archon KB indexed primarily for vision/generative models, not NLP uncertainty quantification.

**Queries Executed**:
- Query 1: "selective prediction uncertainty quantification" → Diffusion models only
- Query 2: "temperature scaling conformal prediction" → Limited calibration code (quantization)
- Query 3: "TruthfulQA benchmark evaluation" → No indexed papers
- Query 4: "AUROC selective prediction abstention" → Diffusion models only
- Query 5: "MC dropout Bayesian uncertainty LLM" → No matches

**Gap Identified**: Archon lacks code examples for UQ methods. Relied on Exa GitHub search instead.

### B. GitHub Implementations (Exa)

**Repository 1: sylinrl/TruthfulQA** (⭐911 - Official)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Query Used**: "TruthfulQA evaluation uncertainty quantification selective prediction GitHub"
- **Relevance**: OFFICIAL TruthfulQA benchmark (author: Stephanie Lin)
- **Used For**: Dataset specification, evaluation protocol
- **Key Findings**:
  - Dataset: TruthfulQA.csv (817 questions, human-annotated)
  - Evaluation: `evaluate.py` with MC1/MC2 tasks
  - Metrics: BLEURT, ROUGE, BLEU, GPT-judge

**Repository 2: insomniac-asif/honest-confidence**
- **URL**: https://github.com/insomniac-asif/honest-confidence
- **Query Used**: "TruthfulQA evaluation uncertainty quantification selective prediction GitHub"
- **Relevance**: Selective prediction on TruthfulQA with calibration + AUROC
- **Used For**: AUROC metric, abstention protocol
- **Key Results**: ECE 0.479 → 0.139 (3.4× improvement), AUROC 0.577 baseline
- **Metrics**: ECE, AUROC, abstention rate, confident-falsehood rate

**Repository 3: mbzuai-nlp/llm-tad-uncertainty** (EMNLP 2025)
- **URL**: https://github.com/mbzuai-nlp/llm-tad-uncertainty
- **Query Used**: "TruthfulQA evaluation uncertainty quantification selective prediction GitHub"
- **Relevance**: Trainable Attention-Based Dependency (TAD) for LLM UQ
- **Used For**: Reference only (supervised method, outside our scope)
- **Models Tested**: LLaMA-3.1, Gemma-2, Qwen-2.5
- **Note**: 100× faster than MC dropout but requires training

**Repository 4: mc-dropout-pytorch** (PyPI Package)
- **URL**: https://pypi.org/project/mc-dropout-pytorch/
- **Query Used**: "temperature scaling conformal prediction MC dropout PyTorch implementation"
- **Relevance**: Clean MC Dropout implementation (Gal & Ghahramani 2016)
- **Used For**: MC dropout pseudo-code
- **Key Code**:
  ```python
  from mc_dropout_pytorch import BayesianMLP, MCDropoutInference
  model = BayesianMLP(dropout_rate=0.1)
  mc = MCDropoutInference(model, num_samples=50, task='classification')
  out = mc(x)
  out.mean, out.variance  # Predictive mean + epistemic uncertainty
  ```

**Repository 5: A-SHOJAEI/adversarial-uncertainty-calibration-for-medical-diagnosis**
- **URL**: https://github.com/A-SHOJAEI/adversarial-uncertainty-calibration-for-medical-diagnosis
- **Query Used**: "temperature scaling conformal prediction MC dropout PyTorch implementation"
- **Relevance**: Combines temperature scaling + MC dropout in unified framework
- **Used For**: Temperature scaling pseudo-code
- **Architecture**: Dual-head (task + adversarial calibration), ResNet-50 backbone
- **Training**: Calibration-aware loss (ECE minimization)
- **Key Insight**: Temperature scaling applied POST-HOC (fits T on calibration set)

**Repository 6: ShahnawazKakarh/retinal-selective-prediction**
- **URL**: https://github.com/ShahnawazKakarh/retinal-selective-prediction
- **Query Used**: "temperature scaling conformal prediction MC dropout PyTorch implementation"
- **Relevance**: Benchmarks all 3 UQ methods on classification
- **Used For**: All 3 UQ method implementations, AUROC computation
- **Key Results**:
  - Temp Scaling (T=2.25): ECE 0.146 → 0.055 (62% reduction)
  - MC Dropout (T=30): Best AURC
  - Conformal (split, α=0.10): 90.2% coverage
- **Code Structure**: `src/uncertainty/` modules, `src/selective/risk_coverage.py` (AUROC)

**Repository 7: Robust Uncertainty via MC-CP** (arXiv 2308.09647)
- **URL**: https://arxiv.org/html/2308.09647
- **Query Used**: "temperature scaling conformal prediction MC dropout PyTorch implementation"
- **Relevance**: Monte Carlo-Conformal Prediction (hybrid MC + CP)
- **Used For**: Adaptive MC dropout concept (early stopping when variance converges)
- **Key Innovation**: Threshold δ + patience P → stop when Var(predictions) < δ for P consecutive passes
- **Efficiency**: Saves computation vs fixed K forward passes

**Repository 8: likenneth/honest_llama**
- **URL**: https://github.com/likenneth/honest_llama/blob/master/utils.py
- **Query Used**: "Llama-3 TruthfulQA benchmark evaluation code"
- **Relevance**: TruthfulQA evaluation for Llama models
- **Used For**: Llama + TruthfulQA integration pattern
- **Key Function**: `alt_tqa_evaluate()` - runs TruthfulQA with HF models
- **Metrics**: MC1/MC2, BLEURT, ROUGE, BLEU, GPT-judge/info

### C. Code Analysis (Serena)

*Skipped* - Code from search results was sufficiently clear. Standard UQ methods well-documented in found repositories.

### D. Papers Referenced (from Phase 2B)

**Guo et al. 2017**: "On Calibration of Modern Neural Networks" (Temperature Scaling)
- Citation count: 9294
- Key contribution: Single-parameter post-hoc calibration with 0× inference overhead

**Kumar et al. 2023**: Conformal Prediction (distribution-free coverage guarantees)
- Citation count: 148

**Gal & Ghahramani 2016**: "Dropout as a Bayesian Approximation"
- MC dropout approximates Bayesian inference via k forward passes

**Lin et al. 2021**: "TruthfulQA: Measuring How Models Mimic Human Falsehoods"
- GitHub stars: 911
- Dataset: 817 human-annotated questions

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-20T02:30:23.201049+00:00

### Workflow History for This Hypothesis

**Event 1**: Hypothesis h-e1 set to IN_PROGRESS
- Timestamp: 2026-08-20T02:30:23.201049+00:00
- Phase: Hypothesis Loop
- Details: External loop starting Phase 2C → 3 → 4 for h-e1

**Event 2**: Phase 2C Experiment Design Started
- Timestamp: 2026-08-20 (current session)
- Phase: Phase 2C
- Status: Completed successfully
- Output: 02c_experiment_brief.md (this document)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
