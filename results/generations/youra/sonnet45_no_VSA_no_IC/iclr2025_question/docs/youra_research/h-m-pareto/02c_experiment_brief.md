# Experiment Design: h-m-pareto

**Date:** 2026-08-20
**Author:** yoon303b@gmail.com
**Hypothesis Statement:** Under the same conditions, if we construct the empirical Pareto frontier from (cost, AUROC) pairs for all 6 UQ methods, then at least 2 methods are Pareto-optimal (no method strictly dominates another with statistical significance p < 0.05), because different UQ mechanisms trade off calibration quality vs computational cost at different efficiency zones.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Cost-performance trade-off analysis

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m-integrated (VALIDATED, PASSED)
**Gate Status:** SHOULD_WORK (non-blocking - negative result is scientifically valuable)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m-pareto
- **Type:** Mechanism
- **Prerequisites:** h-m-integrated

### Gate Condition
SHOULD_WORK: Non-blocking gate. Negative result (|Pareto_set| = 1) is scientifically valuable evidence that one method universally dominates.

---

## Continuation Context

Building on h-m-integrated validation results. Assumes UQ pipeline produces valid uncertainty rankings with AUROC > 0.55 and Spearman ρ > 0.2.

### Previous Hypothesis Results (if applicable)
h-m-integrated validated that all UQ methods produce uncertainty scores correlated with prediction incorrectness. Now testing if cost-performance trade-offs exist.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Pareto frontier UQ cost-performance**
- Limited direct results for Pareto frontier + UQ combination
- Results focused on quantization/optimization trade-offs (not UQ methods)
- Key insight: Cost-performance analysis is domain-general, not UQ-specific

**Query 2: Selective prediction uncertainty methods**
- OpenAI InstructGPT blog post (truthfulness focus)
- OpenReview forum discussing related topics
- Limited specific TruthfulQA selective prediction cases

**Query 3: Temperature scaling, conformal prediction, MC dropout**
- Results focused on attention mechanisms and diffusion models
- No direct UQ method implementation examples in KB
- Suggests UQ methods are well-established (standard ML libraries)

**Key Takeaways:**
- Pareto frontier construction is standard multi-objective optimization
- UQ methods (temp scaling, conformal, MC dropout) are foundational ML techniques
- Implementation should rely on established libraries (sklearn, torch)
- No novel implementation challenges identified

### Archon Code Examples

**Query 1: Pareto frontier AUROC cost analysis**
- Pipeline performance comparison patterns found (IPEX vs baseline)
- Pattern: Time/cost measurement via repeated runs + averaging
- Example structure: warmup → timed evaluation → comparison

**Query 2: AUROC sklearn metrics**
- Limited UQ-specific code examples
- General evaluation patterns: config-based metrics, multi-GPU evaluation
- Standard approach: sklearn.metrics for AUROC computation

**Implementation Patterns Identified:**
1. Cost measurement: Time multiple runs, average over N passes
2. Metrics computation: sklearn.metrics.roc_auc_score for AUROC
3. Comparison: Collect (cost, metric) pairs, construct frontier via dominance check

### Exa GitHub Implementations

**Query 1: Conformal Prediction + Temperature Scaling Implementation**

**Repository 1**: lahavdabah/TS4CP (⭐ not shown, ICML paper)
- **URL**: https://github.com/lahavdabah/TS4CP
- **Relevance**: Directly studies temperature scaling + conformal prediction trade-offs (paper: "On Temperature Scaling and Conformal Prediction of Deep Classifiers")
- **Architecture**: Post-hoc calibration framework, works with any classifier
- **Key Code**: Temperature optimization for AvgSize, TopCovGap, and trade-off (beta parameter)
- **Training Config**: 
  - Methods: LAC, APS, RAPS conformal prediction
  - Beta trade-off: [0,1] (0=AvgSize, 1=TopCovGap)
  - Evaluation: n_eval samples for temperature tuning
- **Dataset**: CIFAR-10 with ResNet-50 shown in examples
- **Results**: Shows non-monotonic trend between temperature and prediction set size

**Repository 2**: atzamis/TorchCP (⭐ not shown, PyTorch library)
- **URL**: https://github.com/atzamis/TorchCP
- **Relevance**: Comprehensive conformal prediction library with temperature scaling (ConfTS method)
- **Architecture**: Modular design - score functions (THR, APS, SAPS, RAPS) + predictors (Split, Clustered, ClassWise)
- **Key Code**: 
  ```python
  from torchcp.classification.score import THR
  from torchcp.classification.predictor import SplitPredictor
  predictor = SplitPredictor(score_function=THR(), model=model)
  predictor.calibrate(cal_dataloader, alpha=0.1)
  predict_sets = predictor.predict(test_instances)
  result_dict = predictor.evaluate(test_dataloader)
  ```
- **Training Methods**: 6 training algorithms (ConfTr, ConfTS, C-Adapter)
- **Dataset**: Supports general PyTorch dataloaders
- **Results**: GPU-accelerated, 90% reduction in inference time on ImageNet

**Query 2: MC Dropout + AUROC Selective Prediction**

**Repository 3**: ShahnawazKakarh/retinal-selective-prediction (⭐ not shown)
- **URL**: https://github.com/ShahnawazKakarh/retinal-selective-prediction
- **Relevance**: Benchmark comparing 5 UQ families (softmax, MC dropout, ensembles, temp scaling, conformal, evidential)
- **Architecture**: EfficientNet-B0 backbone with modular uncertainty methods
- **Key Results**:
  - MC Dropout (T=30): AURC 0.0756 (best across all methods)
  - Temperature Scaling: ECE 0.146→0.055 (62% reduction)
  - Conformal: 90.2% coverage @ α=0.10, avg set size 1.35
  - Softmax baseline: AURC 0.0793
- **Training Config**: T=30 MC dropout passes, mutual information signal
- **Dataset**: APTOS 2019 retinal images
- **Key Insight**: "Three different methods, three different wins" - no universal dominance

**Repository 4**: mkjuergens/Selective-MSMS (⭐ not shown)
- **URL**: https://github.com/mkjuergens/Selective-MSMS
- **Relevance**: Selective prediction for molecular structure retrieval using MC dropout and Laplace uncertainty
- **Architecture**: First and second-order uncertainty representations
- **Dataset**: MassSpecGym benchmark
- **Results**: ~18 GB predictions with MC dropout samples

**Serena Analysis Needed**: False - Code patterns are clear from library documentation

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Analysis**: h-m-pareto is a novel analysis (Pareto frontier for UQ methods), not reproducing a specific paper method.

**Implementation Priority**:
1. **Library** (TorchCP): Well-maintained PyTorch library for conformal prediction + temperature scaling
2. **Community** (retinal-selective-prediction): Benchmark comparing 5 UQ families with validated AUROC results
3. **Paper Author** (lahavdabah/TS4CP): Temperature scaling + conformal prediction trade-off analysis (ICML)

**Recommended Implementation Path:**
- **Primary**: TorchCP library for conformal prediction + sklearn for AUROC + custom Pareto analysis
- **Fallback**: Manual implementation based on retinal-selective-prediction patterns
- **Justification**: 
  - TorchCP provides GPU-accelerated, validated implementations of conformal prediction methods
  - Retinal-selective-prediction validates that MC dropout (T=30) achieves best AURC
  - Pareto frontier construction is standard multi-objective optimization (no special library needed)
  - TS4CP confirms temperature scaling creates trade-offs (non-monotonic trend)

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear (TorchCP library documentation and retinal-selective-prediction benchmark provide complete implementation patterns)

---

## Experiment Specification

### Dataset

**Primary Dataset**: TruthfulQA
**Type**: standard (human-annotated QA benchmark)
**Size**: 817 questions across 38 categories
**Task**: Selective prediction on generative QA (truthfulness evaluation)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthfulqa/truthful_qa`
- Config: `generation` (not multiple_choice)
- Split: `validation` (817 examples)
- Code: 
  ```python
  from datasets import load_dataset
  ds = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")
  ```

**Data Fields**:
- `question`: Adversarial question string
- `best_answer`: Single best truthful answer
- `correct_answers`: List of acceptable truthful answers
- `incorrect_answers`: List of common false answers
- `category`: One of 38 categories (e.g., Misconceptions, Health, Law)

**Calibration Dataset**: HaluEval
**Type**: standard (hallucination evaluation)
**Size**: ~10k samples
**Purpose**: Calibration set for temperature scaling and conformal prediction
**Note**: Used for calibration only, TruthfulQA is test set

**Hypothesis Fit**: 
- IV (UQ method) applied to all 817 questions
- DV (AUROC) computed from uncertainty scores vs correctness (correct_answers as ground truth)
- Enables Pareto frontier construction from (cost, AUROC) pairs

### Models

#### Baseline Model

**Architecture**: Llama-3.1-8B-Instruct
**Type**: Pre-trained instruction-tuned autoregressive LLM
**Parameters**: 8 billion
**Context Window**: 128k tokens

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-3.1-8B-Instruct`
- Access: Requires Meta license agreement + HF token
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-3.1-8B-Instruct",
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
  ```

**Modifications for Hypothesis**: 
- Enable dropout for MC dropout (set `model.config.use_cache = False` and `model.eval()` with dropout enabled)
- No architecture changes (fixed baseline across all UQ methods)

#### Proposed Model

**Architecture:** All 6 UQ methods (temperature scaling, conformal prediction, MC dropout k=1,3,5,10)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Pareto Frontier Construction for UQ Methods
# Based on: TorchCP library + retinal-selective-prediction benchmark

class ParetoFrontierAnalyzer:
    """
    Constructs empirical Pareto frontier from (cost, AUROC) pairs.
    Tests H1 (MC k=5 highest), H2 (temp scaling competitive), H3 (trade-off exists).
    """
    def __init__(self, methods, alpha=0.05, n_seeds=3):
        self.methods = methods  # List of UQ method names
        self.alpha = alpha      # Significance level for paired t-test
        self.n_seeds = n_seeds  # Random seeds for AUROC estimation
    
    def compute_cost_auroc_pairs(self, model, dataset, calibration_set):
        """
        Args:
            model: Llama-3.1-8B-Instruct
            dataset: TruthfulQA (817 questions)
            calibration_set: HaluEval (~10k samples)
        Returns:
            results: Dict[method_name, (cost, auroc_mean, auroc_std)]
        """
        results = {}
        for method in self.methods:
            costs, aurocs = [], []
            for seed in range(self.n_seeds):
                # Generate uncertainty scores per method
                if method == "temperature_scaling":
                    temp = calibrate_temperature(model, calibration_set)
                    scores, preds = apply_temp_scaling(model, dataset, temp)
                    cost = 1.0  # 1× baseline (post-hoc, no extra inference)
                elif method == "conformal_prediction":
                    threshold = calibrate_conformal(model, calibration_set, alpha=0.1)
                    scores, preds = apply_conformal(model, dataset, threshold)
                    cost = 1.0  # 1× baseline (post-hoc)
                elif method.startswith("mc_dropout"):
                    k = int(method.split("_k")[-1])  # Extract k from "mc_dropout_k5"
                    scores, preds = apply_mc_dropout(model, dataset, n_passes=k)
                    cost = float(k)  # k× baseline (k forward passes)
                
                # Compute AUROC: uncertainty vs correctness
                correctness = evaluate_correctness(preds, dataset.correct_answers)
                auroc = roc_auc_score(y_true=correctness, y_score=scores)
                
                costs.append(cost)
                aurocs.append(auroc)
            
            results[method] = (np.mean(costs), np.mean(aurocs), np.std(aurocs))
        
        return results
    
    def construct_pareto_frontier(self, results):
        """
        Args:
            results: Dict[method, (cost, auroc_mean, auroc_std)]
        Returns:
            pareto_set: List of Pareto-optimal method names
        """
        pareto_set = []
        for i, method_i in enumerate(self.methods):
            cost_i, auroc_i, std_i = results[method_i]
            dominated = False
            
            # Check if any method j dominates i
            for j, method_j in enumerate(self.methods):
                if i == j:
                    continue
                cost_j, auroc_j, std_j = results[method_j]
                
                # Dominance: cost_j <= cost_i AND auroc_j > auroc_i (statistically significant)
                if cost_j <= cost_i:
                    # Paired t-test for AUROC difference
                    auroc_samples_i = [auroc_i + np.random.normal(0, std_i) for _ in range(self.n_seeds)]
                    auroc_samples_j = [auroc_j + np.random.normal(0, std_j) for _ in range(self.n_seeds)]
                    t_stat, p_val = ttest_rel(auroc_samples_j, auroc_samples_i)
                    
                    if p_val < self.alpha and auroc_j > auroc_i:
                        dominated = True
                        break
            
            if not dominated:
                pareto_set.append(method_i)
        
        return pareto_set

# Integration: Standalone analysis after UQ pipeline (h-m-integrated) completes
# No model architecture modification - pure post-hoc analysis
```

### Training Protocol

**No Training Required** - Post-hoc analysis only

**Calibration**:
- **Dataset**: HaluEval (~10k samples) for temperature scaling + conformal prediction
- **Method**: 
  - Temperature scaling: Grid search over T ∈ [0.5, 5.0] to minimize NLL
  - Conformal prediction: Compute α-quantile threshold (α=0.1)
- **Source**: TorchCP library calibration protocol

**Inference**:
- **Model**: Llama-3.1-8B-Instruct (frozen, no fine-tuning)
- **Batch Size**: 8 (memory constraint for 8B model)
- **Seeds**: 3 (42, 123, 456) for AUROC variance estimation
- **Precision**: bfloat16 (as per Llama-3.1 default)

**UQ Methods**:
1. Temperature scaling: 1× cost (post-hoc)
2. Conformal prediction: 1× cost (post-hoc)
3. MC dropout k=1: 1× cost (baseline)
4. MC dropout k=3: 3× cost
5. MC dropout k=5: 5× cost (expected highest AUROC per H1)
6. MC dropout k=10: 10× cost

**Source**: Phase 2B verification plan + retinal-selective-prediction benchmark (MC dropout T=30 showed best AURC)

### Evaluation

**Primary Metric**: AUROC (Area Under ROC Curve for selective prediction)
**Task**: Binary classification (correct vs incorrect predictions)

**Metrics**:
1. **AUROC** (primary success criterion ≥ 0.70): Discrimination ability between correct/incorrect
2. **Spearman ρ**: Correlation between uncertainty and incorrectness (validation check > 0.2)
3. **FLOPs Cost**: Inference cost normalized to 1.0× baseline
4. **Pareto Set Size**: Number of Pareto-optimal methods (success: ≥ 2)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (uncertainty-based selective prediction)
- Library: sklearn.metrics (AUROC, ROC curve), scipy.stats (Spearman, t-test)
- Code:
  ```python
  from sklearn.metrics import roc_auc_score, roc_curve
  from scipy.stats import spearmanr, ttest_rel
  
  # AUROC for selective prediction
  auroc = roc_auc_score(y_true=correctness_labels, y_score=uncertainty_scores)
  
  # Spearman correlation
  rho, p_value = spearmanr(uncertainty_scores, incorrectness_binary)
  
  # Paired t-test for dominance check
  t_stat, p_val = ttest_rel(auroc_method_i, auroc_method_j)
  ```

**Statistical Significance**: Paired t-test (α=0.05, n=3 seeds) for Pareto dominance determination

### Visualization Requirements

#### Required Figure (Mandatory)
- **Pareto Frontier Plot**: (cost, AUROC) scatter plot with Pareto-optimal methods highlighted

#### Additional Figures (LLM Autonomous)

Based on Pareto frontier analysis and cost-performance trade-off hypothesis:

1. **Pareto Frontier Scatter Plot**:
   - X-axis: Normalized cost (FLOPs, 1.0× baseline)
   - Y-axis: AUROC (selective prediction)
   - Points: 6 UQ methods with error bars (n=3 seeds)
   - Highlight: Pareto-optimal methods (green), dominated methods (red)
   - Annotations: Method names, (cost, AUROC) values

2. **AUROC Bar Chart with Statistical Significance**:
   - X-axis: 6 UQ methods (ordered by cost)
   - Y-axis: AUROC mean ± std (n=3 seeds)
   - Threshold line: AUROC ≥ 0.70 (success criterion from h-e1)
   - Significance brackets: Paired t-test results (α=0.05)

3. **Cost vs AUROC Trade-off Curves**:
   - X-axis: Normalized cost (1× to 10×)
   - Y-axis: AUROC improvement over baseline
   - Lines: MC dropout (k=1,3,5,10), temperature scaling, conformal prediction
   - Highlight: Diminishing returns zone (MC k>5)

4. **Spearman Correlation Heatmap**:
   - Rows: 6 UQ methods
   - Columns: Uncertainty score vs incorrectness
   - Values: Spearman ρ (validation check > 0.2 from h-m-integrated)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **Mechanism Exists**: Pareto dominance check implemented (cost_j ≤ cost_i AND auroc_j > auroc_i)
- **Mechanism Isolatable**: Each UQ method produces (cost, AUROC) pair independently
- **Baseline Measurable**: Softmax baseline (1× cost) provides comparison reference

### Architecture Compatibility
- No architecture modification required - standalone analysis
- Requires: Model outputs (predictions), ground truth labels (TruthfulQA correct_answers)
- Compatible with any LLM (Llama-3.1-8B-Instruct tested)

### Activation Indicators
1. **Log Message**: "Pareto frontier constructed: |Pareto_set| = X methods"
2. **Tensor Shape Check**: results dict has 6 entries (one per method)
3. **Metric Delta Expected**: |AUROC_mc_k5 - AUROC_temp_scaling| should be measurable (non-zero)

### Mechanism Verification Code
```python
# Verify Pareto frontier construction works
assert len(results) == 6, f"Expected 6 methods, got {len(results)}"
assert all(0 <= auroc <= 1.0 for _, auroc, _ in results.values()), "AUROC out of bounds"
assert len(pareto_set) >= 1, "Empty Pareto set - all methods dominated (impossible)"

# Check cost ordering
costs = [results[m][0] for m in ["temperature_scaling", "mc_dropout_k1", "mc_dropout_k3", "mc_dropout_k5", "mc_dropout_k10"]]
assert costs == sorted(costs), "Cost values not increasing as expected"

# H1 check: MC k=5 should have highest or near-highest AUROC
mc_k5_auroc = results["mc_dropout_k5"][1]
max_auroc = max(auroc for _, auroc, _ in results.values())
assert mc_k5_auroc >= max_auroc - 0.05, "H1 violation: MC k=5 not competitive"
```

### Success Criteria
- **Primary**: |Pareto_set| ≥ 2 (H3 confirmed: cost-performance trade-off exists)
- **Secondary**: 
  - H1: MC k=5 has highest AUROC among all methods
  - H2: |AUROC_temp_scaling - AUROC_mc_k5| ≤ 0.05 (temp scaling competitive)

---

## Appendix: Reference Implementations

### Primary References

1. **TorchCP** (https://github.com/atzamis/TorchCP)
   - Library: PyTorch-native conformal prediction
   - Methods: LAC, APS, SAPS, RAPS score functions
   - Usage: Split/Clustered/ClassWise predictors
   - Relevance: Conformal prediction implementation

2. **retinal-selective-prediction** (https://github.com/ShahnawazKakarh/retinal-selective-prediction)
   - Benchmark: 5 UQ families (softmax, MC dropout, ensembles, temp scaling, conformal)
   - Results: MC dropout T=30 → AURC 0.0756 (best), temp scaling → ECE 0.146→0.055
   - Relevance: Validates MC dropout superior AURC, temp scaling calibration improvement

3. **TS4CP** (https://github.com/lahavdabah/TS4CP)
   - Paper: "On Temperature Scaling and Conformal Prediction of Deep Classifiers" (ICML)
   - Methods: Temperature optimization for AvgSize, TopCovGap, trade-off (beta)
   - Results: Non-monotonic trend between temperature and prediction set size
   - Relevance: Confirms temperature scaling creates cost-performance trade-offs

### Implementation Notes

- Use sklearn.metrics.roc_auc_score for AUROC computation
- Use scipy.stats.ttest_rel for paired t-test (dominance check)
- Use scipy.stats.spearmanr for correlation validation (h-m-integrated prerequisite)
- HuggingFace datasets for TruthfulQA loading (truthfulqa/truthful_qa, generation config)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-20T03:27:16+00:00

### Workflow History for This Hypothesis
- 2026-08-20T03:27:16: h-m-pareto set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
