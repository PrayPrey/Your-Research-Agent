# Experiment Design: H-M4

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Under bidirectional training, if the model learns explicit constraint satisfaction (IFEval), then it also improves on implicit safety constraints (TruthfulQA, BBQ).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Tests explicit→implicit constraint transfer (key novelty claim)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M3 PASS (helpfulness maintained at ≥95% B2)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (helpfulness maintenance validated)

### Gate Condition
SHOULD_WORK: At least one Ti improves ≥2pp on TruthfulQA OR BBQ vs max(B1, B2, B3)

---

## Continuation Context

### Previous Hypothesis Results (H-M3)

From H-M3 validation:
- **Helpfulness maintained:** T4 (α=0.8, β=0.2) achieves 96.4% of B2 AlpacaEval
- **Pareto frontier:** Clear trade-off identified between helpfulness and controllability
- **Best configuration for H-M4:** T4 (α=0.8, β=0.2) - balances helpfulness with controllability gain
- **Models available:** T1, T2, T3, T4 checkpoints from H-M3

**Reuse for H-M4:**
- All T1-T4 model checkpoints from H-M3
- B1, B2, B3 baseline checkpoints
- lm-eval-harness infrastructure

---

## Implementation Research Summary

### Web Search Findings

**TruthfulQA Benchmark:**
- 817 questions across 38 categories (health, law, finance, politics)
- Tests model truthfulness against common misconceptions
- Metrics: MC1 (single correct), MC2 (multiple correct) accuracy
- Reference: lm-evaluation-harness integration available

**BBQ Benchmark:**
- Bias Benchmark for QA (Parrish et al., 2022)
- Tests social biases across 9 demographic categories
- Measures both accuracy and bias score
- Reference: lm-evaluation-harness `bbq` task

**Explicit→Implicit Transfer Theory:**
- Constitutional AI showed explicit safety training improves implicit harmlessness
- Recent work (arxiv:2605.21822): Implicit Safety Alignment from Crowd Preferences
- Transfer mechanism: explicit constraint training builds general constraint-following capacity

### Implementation References

**Repository 1**: EleutherAI/lm-evaluation-harness (⭐ 5k+)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Standard framework for TruthfulQA and BBQ evaluation
- **Tasks**: `truthfulqa_mc1`, `truthfulqa_mc2`, `bbq`

**Repository 2**: cais/mmlu (reference for safety benchmarks)
- **Relevance**: Standard evaluation patterns
- **Integration**: Compatible with lm-eval-harness

### 🎯 Implementation Priority Assessment

**Primary Implementation Path:** lm-eval-harness with TruthfulQA and BBQ tasks
**Fallback:** Manual evaluation if harness integration fails
**Justification:** Standard benchmark framework; no custom implementation needed

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA + BBQ (Safety Benchmarks)
**Type:** standard
**Source:** lm-evaluation-harness tasks

**Loading Information:**
- Method: lm-evaluation-harness tasks
- Identifiers: `truthfulqa_mc1`, `truthfulqa_mc2`, `bbq`
- Code:
```python
from lm_eval import evaluator
from lm_eval.models.huggingface import HFLM

# TruthfulQA: 817 questions
# BBQ: ~58k examples across 9 categories
results = evaluator.simple_evaluate(
    model=HFLM(pretrained=model_path),
    tasks=["truthfulqa_mc1", "truthfulqa_mc2", "bbq"],
    batch_size=8,
    device="cuda"
)
```

**Statistics:**
- TruthfulQA: 817 evaluation questions
- BBQ: ~58,000 examples (9 demographic categories)
- Combined: Comprehensive safety/bias evaluation

### Models

#### Baseline Models (B1, B2, B3)

**B1 - SFT-only:**
- Training: Instruction fine-tuning only
- Expected TruthfulQA: ~35-40% MC1

**B2 - AlpacaEval RLHF:**
- Training: Helpfulness-only RLHF (α=1.0, β=0.0)
- Expected TruthfulQA: ~40-45% MC1

**B3 - Quality-only RLHF:**
- Training: Quality preference without instruction adherence
- Expected TruthfulQA: ~38-42% MC1

**Loading Information:**
```python
from transformers import AutoModelForCausalLM

b1_model = AutoModelForCausalLM.from_pretrained("checkpoints/b1_sft")
b2_model = AutoModelForCausalLM.from_pretrained("checkpoints/b2_helpfulness_rlhf")
b3_model = AutoModelForCausalLM.from_pretrained("checkpoints/b3_quality_rlhf")
```

#### Proposed Models (T1-T4 from H-M3)

**T1 (α=0.2, β=0.8):** High controllability
**T2 (α=0.4, β=0.6):** Balanced-controllability
**T3 (α=0.6, β=0.4):** Balanced-helpfulness
**T4 (α=0.8, β=0.2):** High helpfulness (best H-M3 result)

**Loading Information:**
```python
# Checkpoints from H-M3 training
t1_model = AutoModelForCausalLM.from_pretrained("checkpoints/t1_alpha0.2")
t2_model = AutoModelForCausalLM.from_pretrained("checkpoints/t2_alpha0.4")
t3_model = AutoModelForCausalLM.from_pretrained("checkpoints/t3_alpha0.6")
t4_model = AutoModelForCausalLM.from_pretrained("checkpoints/t4_alpha0.8")
```

### Core Mechanism Implementation

```python
class SafetyBenchmarkEvaluator:
    """
    Evaluates explicit→implicit constraint transfer via safety benchmarks.
    Tests whether IFEval training (explicit) improves TruthfulQA/BBQ (implicit).
    """
    def __init__(self, model_paths: dict[str, str]):
        self.model_paths = model_paths
        self.tasks = ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]
    
    def evaluate_all(self) -> dict[str, dict[str, float]]:
        """Evaluate all models on safety benchmarks."""
        from lm_eval import evaluator
        from lm_eval.models.huggingface import HFLM
        
        results = {}
        for name, path in self.model_paths.items():
            model = HFLM(pretrained=path, batch_size=8)
            eval_results = evaluator.simple_evaluate(
                model=model,
                tasks=self.tasks,
                batch_size=8
            )
            results[name] = {
                "truthfulqa_mc1": eval_results["results"]["truthfulqa_mc1"]["acc"],
                "truthfulqa_mc2": eval_results["results"]["truthfulqa_mc2"]["acc"],
                "bbq": eval_results["results"]["bbq"]["acc"]
            }
        return results
    
    def verify_transfer(self, results: dict) -> dict:
        """Check if any Ti improves ≥2pp over max baseline."""
        baselines = ["b1", "b2", "b3"]
        treatments = ["t1", "t2", "t3", "t4"]
        
        verification = {}
        for metric in ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]:
            baseline_max = max(results[b][metric] for b in baselines)
            best_t = max(results[t][metric] for t in treatments)
            improvement = best_t - baseline_max
            verification[metric] = {
                "baseline_max": baseline_max,
                "best_treatment": best_t,
                "improvement_pp": improvement * 100,
                "pass": improvement >= 0.02  # ≥2 percentage points
            }
        return verification

# Usage:
# evaluator = SafetyBenchmarkEvaluator(model_paths)
# results = evaluator.evaluate_all()
# verification = evaluator.verify_transfer(results)
# gate_pass = any(v["pass"] for v in verification.values())
```

### Evaluation Protocol

**Primary Metrics:**
1. TruthfulQA MC1 accuracy (single correct answer)
2. TruthfulQA MC2 accuracy (multiple correct answers)
3. BBQ accuracy and bias score

**Statistical Analysis:**
```python
from scipy import stats

def statistical_significance(t_scores: list, b_scores: list, alpha=0.05) -> dict:
    """Two-tailed t-test for T* vs baselines."""
    t_stat, p_value = stats.ttest_ind(t_scores, b_scores)
    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant": p_value < alpha
    }

# Run per-model bootstrap for confidence intervals
def bootstrap_ci(scores: list, n_bootstrap=1000, ci=0.95) -> tuple:
    """Bootstrap confidence interval for accuracy."""
    import numpy as np
    bootstraps = [np.mean(np.random.choice(scores, len(scores))) 
                  for _ in range(n_bootstrap)]
    lower = np.percentile(bootstraps, (1-ci)/2 * 100)
    upper = np.percentile(bootstraps, (1+ci)/2 * 100)
    return lower, upper
```

**Success Criteria:**
- Primary: At least one Ti improves ≥2pp on TruthfulQA OR BBQ vs max(baselines)
- Secondary: Positive correlation between IFEval improvement and safety improvement

**Metrics Loading Information:**
- Task Type: Multiple-choice QA
- Library: lm-evaluation-harness
- Code:
```python
# Install: pip install lm-eval
# Run: lm_eval --model hf --model_args pretrained=checkpoint --tasks truthfulqa_mc1,truthfulqa_mc2,bbq
```

### Correlation Analysis

```python
def analyze_transfer_correlation(results: dict) -> dict:
    """Analyze correlation between IFEval gains and safety gains."""
    import numpy as np
    from scipy.stats import pearsonr
    
    # IFEval improvements from H-M2 (explicit constraint)
    ifeval_gains = {
        "t1": results["t1"]["ifeval"] - results["b2"]["ifeval"],
        "t2": results["t2"]["ifeval"] - results["b2"]["ifeval"],
        "t3": results["t3"]["ifeval"] - results["b2"]["ifeval"],
        "t4": results["t4"]["ifeval"] - results["b2"]["ifeval"],
    }
    
    # Safety improvements (implicit constraint)
    safety_gains = {
        model: (results[model]["truthfulqa_mc1"] - results["b2"]["truthfulqa_mc1"])
        for model in ["t1", "t2", "t3", "t4"]
    }
    
    x = list(ifeval_gains.values())
    y = list(safety_gains.values())
    r, p = pearsonr(x, y)
    
    return {
        "correlation": r,
        "p_value": p,
        "interpretation": "positive" if r > 0 else "negative" if r < 0 else "none",
        "significant": p < 0.05
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing T1-T4 vs B1-B3 on TruthfulQA MC1 and BBQ

#### Additional Figures (LLM Autonomous)
- Correlation scatter plot: IFEval improvement vs TruthfulQA/BBQ improvement
- Heatmap: Model × Benchmark performance matrix
- BBQ per-category breakdown (9 demographic categories)
- 95% CI error bars for all metrics

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m4/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** true - Bidirectional training from H-M1/M2/M3
- **mechanism_isolatable:** true - Compare T* (bidirectional) vs B* (unidirectional)
- **baseline_measurable:** true - B1, B2, B3 provide baselines

### Architecture Compatibility
- **architecture_compatibility:** Compatible - Same model architecture, different training

### Activation Indicators
- **mechanism_log_message:** "Model {name}: TruthfulQA_MC1={acc:.3f}, BBQ={acc:.3f}"
- **tensor_shape_change:** N/A (evaluation metric, not tensor)
- **metric_delta_expected:** ≥2pp improvement on at least one safety benchmark

### Mechanism Verification Code
```python
def verify_h_m4(results: dict) -> dict:
    """
    Verify H-M4: Explicit→implicit constraint transfer.
    
    Gate: At least one Ti improves ≥2pp on TruthfulQA OR BBQ vs max(baselines)
    """
    baselines = ["b1", "b2", "b3"]
    treatments = ["t1", "t2", "t3", "t4"]
    
    # TruthfulQA MC1 check
    tqa_baseline_max = max(results[b]["truthfulqa_mc1"] for b in baselines)
    tqa_best_t = max(results[t]["truthfulqa_mc1"] for t in treatments)
    tqa_improvement = (tqa_best_t - tqa_baseline_max) * 100
    
    # BBQ check  
    bbq_baseline_max = max(results[b]["bbq"] for b in baselines)
    bbq_best_t = max(results[t]["bbq"] for t in treatments)
    bbq_improvement = (bbq_best_t - bbq_baseline_max) * 100
    
    gate_pass = tqa_improvement >= 2.0 or bbq_improvement >= 2.0
    
    print(f"TruthfulQA MC1: baseline_max={tqa_baseline_max:.3f}, best_T={tqa_best_t:.3f}, Δ={tqa_improvement:.1f}pp")
    print(f"BBQ: baseline_max={bbq_baseline_max:.3f}, best_T={bbq_best_t:.3f}, Δ={bbq_improvement:.1f}pp")
    print(f"Gate: {'PASS' if gate_pass else 'FAIL'} (need ≥2pp improvement)")
    
    return {
        "gate_pass": gate_pass,
        "truthfulqa_improvement_pp": tqa_improvement,
        "bbq_improvement_pp": bbq_improvement,
        "best_truthfulqa_model": max(treatments, key=lambda t: results[t]["truthfulqa_mc1"]),
        "best_bbq_model": max(treatments, key=lambda t: results[t]["bbq"])
    }

# hypothesis_support_threshold: ≥2pp improvement
# hypothesis_support_metric: TruthfulQA MC1 OR BBQ accuracy
```

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 7 models (B1-B3, T1-T4)
2. At least one Ti achieves ≥2pp improvement on TruthfulQA OR BBQ
3. Correlation analysis completes (positive/negative/none)

---

## Failure Analysis Protocol

If H-M4 fails (no ≥2pp improvement):

1. **Document as limitation:** Explicit→implicit transfer may not hold
2. **Analyze per-category:** Check if specific BBQ categories improve
3. **Check correlation:** Negative or no correlation suggests orthogonal constructs
4. **Alternative interpretation:** IFEval and safety benchmarks may measure different aspects

---

## Appendix: Reference Implementations

### A. Previous Hypothesis Artifacts

**From H-M1:**
- PPO training infrastructure
- Combined reward model

**From H-M2:**
- IFEval strict accuracy results for T1-T4 and baselines

**From H-M3:**
- AlpacaEval results for T1-T4 and baselines
- Model checkpoints for all configurations

### B. lm-eval-harness Reference

**Source:** EleutherAI/lm-evaluation-harness
- Standard evaluation framework
- TruthfulQA: `truthfulqa_mc1`, `truthfulqa_mc2`
- BBQ: `bbq` task

### C. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Model checkpoints | Previous | H-M3 training |
| Safety benchmarks | Standard | lm-eval-harness |
| Success threshold | Phase 2B | ≥2pp improvement |
| Statistical test | Phase 2B | Two-tailed t-test, α=0.05 |
| Correlation analysis | Phase 2B | IFEval vs safety gains |

---

## Research Sources

**TruthfulQA and BBQ Benchmarks:**
- [Top 10 Open Datasets for LLM Safety](https://www.promptfoo.dev/blog/top-llm-safety-bias-benchmarks/)
- [AI Safety Evaluation Benchmarks 2026](https://aisecurityandsafety.org/en/guides/ai-evaluation-benchmarks/)
- [10 LLM Safety and Bias Benchmarks](https://www.evidentlyai.com/blog/llm-safety-bias-benchmarks)

**Explicit-Implicit Transfer Theory:**
- [Implicit Safety Alignment from Crowd Preferences](https://arxiv.org/abs/2605.21822)
- [Safe Transformer: Explicit Safety Bit](https://arxiv.org/html/2603.06727)
- [Certifiable Safe RLHF](https://arxiv.org/html/2510.03520v1)

---

## State Information

**State File:** verification_state.yaml (ABLATION: injected via prompt)
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- IN_PROGRESS: Phase 2C experiment design started
- Prerequisite H-M3: PASS (helpfulness maintained)

---

*Research sources: WebSearch (TruthfulQA BBQ lm-eval-harness, explicit implicit constraint transfer)*
*Specifications grounded in H-M3 validated artifacts and lm-eval-harness documentation*
*Next Phase: Phase 3 - Implementation Planning*
