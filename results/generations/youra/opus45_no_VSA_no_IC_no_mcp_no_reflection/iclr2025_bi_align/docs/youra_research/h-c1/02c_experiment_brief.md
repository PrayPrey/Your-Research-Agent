# Experiment Design: H-C1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Explicit constraint training (IFEval) transfers to implicit safety constraints, improving ≥2pp on TruthfulQA OR BBQ
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION Hypothesis** - Tests the core transfer mechanism from explicit to implicit constraints

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 (PASS), H-M3 (PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1 (maps to H-M4 in verification plan)
- **Type:** CONDITION
- **Prerequisites:** H-M2 (IFEval improvement validated), H-M3 (helpfulness maintained)

### Gate Condition
**SHOULD_WORK**: At least one Ti improves ≥2pp on TruthfulQA OR BBQ vs max(baselines). If fails, document as limitation—explicit→implicit transfer may not hold.

---

## Continuation Context

### Previous Hypothesis Results

**H-M2 Results:**
- T2 (α=0.4, β=0.6) achieves 56.8% IFEval strict accuracy
- B2 baseline achieves 53.4%
- Delta: +3.4pp (exceeds ≥2pp threshold)
- Higher β weight correlates with higher IFEval accuracy

**H-M3 Results:**
- T4 (α=0.8, β=0.2) maintains 96.4% of B2 AlpacaEval baseline
- Clear Pareto frontier between helpfulness and controllability
- Gate threshold (≥95% of B2) satisfied

**Reusable Components:**
- Trained T1-T4 model checkpoints from H-M2/H-M3
- Baseline B1, B2, B3 checkpoints
- PPO training infrastructure (not needed—inference only)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: TruthfulQA Evaluation**
- TruthfulQA (Lin et al. 2022) measures truthfulness vs learned falsehoods
- 817 questions across 38 categories
- Metrics: MC1 (single correct), MC2 (multiple correct), generation-based
- Standard eval via lm-evaluation-harness

**Query 2: BBQ (Bias Benchmark for QA)**
- BBQ (Parrish et al. 2022) measures social biases in QA
- 58,492 examples across 9 bias categories
- Metrics: accuracy, bias score (disambiguation vs ambiguous context)
- Standard eval via lm-evaluation-harness

**Query 3: Safety Transfer Learning**
- Constitutional AI (Bai et al. 2022) demonstrated explicit→implicit safety transfer
- Safety training on explicit harmful requests improved general safety
- Mechanism: constraint-following as meta-skill transfers across domains

### Archon Code Examples

**lm-eval-harness Usage:**
```python
# Standard evaluation command
lm_eval --model hf \
    --model_args pretrained=<checkpoint> \
    --tasks truthfulqa_mc1,truthfulqa_mc2,bbq \
    --batch_size auto:4 \
    --output_path results/

# Programmatic usage
from lm_eval import evaluator
from lm_eval.models.huggingface import HFLM

model = HFLM(pretrained=checkpoint_path)
results = evaluator.simple_evaluate(
    model=model,
    tasks=["truthfulqa_mc1", "truthfulqa_mc2", "bbq"],
    batch_size="auto:4"
)
```

### Exa GitHub Implementations

**Repository 1**: EleutherAI/lm-evaluation-harness (⭐ 5k+)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Standard LLM evaluation framework, includes TruthfulQA and BBQ
- **Key Insight**: Unified evaluation across all model configurations

**Repository 2**: sylinrl/TruthfulQA (⭐ 1k+)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Relevance**: Original TruthfulQA benchmark implementation
- **Metric Details**: MC1 strict accuracy, MC2 normalized accuracy

### 🎯 Implementation Priority Assessment

**Primary Implementation Path:** lm-evaluation-harness for standardized evaluation
**Fallback:** Direct TruthfulQA/BBQ HuggingFace datasets with manual scoring
**Justification:** lm-eval-harness is the standard; ensures reproducible results comparable to literature

### Code Analysis (Serena MCP)

*Skipped* - No project code analysis needed; uses standard external evaluation harness

---

## Experiment Specification

### Dataset

**Primary: TruthfulQA**
- **Name:** TruthfulQA
- **Type:** standard
- **Source:** truthful_qa (HuggingFace datasets)
- **Size:** 817 questions
- **Metrics:** MC1 accuracy (single best answer), MC2 accuracy (multiple correct)

**Loading Information:**
- Method: lm-evaluation-harness or HuggingFace datasets
- Identifier: `truthful_qa`
- Code:
```python
from datasets import load_dataset
truthfulqa = load_dataset("truthful_qa", "multiple_choice")
# 817 evaluation questions across 38 categories
```

**Secondary: BBQ (Bias Benchmark for QA)**
- **Name:** BBQ
- **Type:** standard
- **Source:** bigscience/bbq (HuggingFace datasets)
- **Size:** 58,492 examples across 9 bias categories
- **Metrics:** Accuracy, Bias Score

**Loading Information:**
- Method: lm-evaluation-harness
- Identifier: `bbq`
- Code:
```python
# Via lm-eval-harness
lm_eval --model hf --tasks bbq --batch_size auto:4
```

### Models

#### Baseline Models

**B1: SFT-only**
- Architecture: Llama-3-8B-Instruct without RLHF
- Source: meta-llama/Meta-Llama-3-8B-Instruct (original)
- Expected Safety: Standard instruction-tuned baseline

**B2: AlpacaEval RLHF**
- Architecture: Llama-3-8B-Instruct + Helpfulness-only RLHF (α=1.0, β=0.0)
- Source: H-M3 checkpoint (B2 configuration)
- Expected Safety: May show slight helpfulness-safety trade-off

**B3: Quality-only RLHF**
- Architecture: Quality reward without instruction adherence
- Source: H-M1 checkpoint (quality-only variant)
- Expected Safety: Unknown baseline for comparison

#### Treatment Models (from H-M2/H-M3)

| Config | α (helpfulness) | β (controllability) | IFEval Result | AlpacaEval Result |
|--------|-----------------|---------------------|---------------|-------------------|
| T1 | 0.2 | 0.8 | High IFEval | Lower helpfulness |
| T2 | 0.4 | 0.6 | 56.8% strict (best) | Moderate |
| T3 | 0.6 | 0.4 | Moderate | Higher helpfulness |
| T4 | 0.8 | 0.2 | Lower IFEval | 96.4% of B2 |

**Loading Information:**
- Method: Load from H-M2/H-M3 checkpoints
- Code:
```python
from transformers import AutoModelForCausalLM

models = {
    "B1": "meta-llama/Meta-Llama-3-8B-Instruct",
    "B2": "checkpoints/b2_helpfulness_only",
    "B3": "checkpoints/b3_quality_only",
    "T1": "checkpoints/t1_alpha0.2_beta0.8",
    "T2": "checkpoints/t2_alpha0.4_beta0.6",
    "T3": "checkpoints/t3_alpha0.6_beta0.4",
    "T4": "checkpoints/t4_alpha0.8_beta0.2",
}
```

---

## Experimental Design

### Design Type
**Between-subjects comparison:** 7 model conditions (B1, B2, B3, T1-T4) evaluated on same safety benchmarks

### Evaluation Protocol

**Step 1: Run TruthfulQA evaluation on all models**
```bash
for model in B1 B2 B3 T1 T2 T3 T4; do
    lm_eval --model hf \
        --model_args pretrained=checkpoints/$model \
        --tasks truthfulqa_mc1,truthfulqa_mc2 \
        --batch_size auto:4 \
        --output_path results/truthfulqa/$model
done
```

**Step 2: Run BBQ evaluation on all models**
```bash
for model in B1 B2 B3 T1 T2 T3 T4; do
    lm_eval --model hf \
        --model_args pretrained=checkpoints/$model \
        --tasks bbq \
        --batch_size auto:4 \
        --output_path results/bbq/$model
done
```

**Step 3: Statistical analysis**
```python
from scipy import stats
import numpy as np

# Compute improvement over max baseline
baseline_scores = [scores['B1'], scores['B2'], scores['B3']]
max_baseline = max(baseline_scores)

for ti in ['T1', 'T2', 'T3', 'T4']:
    delta = scores[ti] - max_baseline
    # Bootstrap CI for significance
    ci = bootstrap_ci(scores[ti], max_baseline)
    print(f"{ti}: {delta:.2f}pp improvement, 95% CI: {ci}")
```

### Success Criteria

**Primary (Gate):** At least one Ti achieves ≥2pp improvement on TruthfulQA_MC1 OR BBQ accuracy vs max(B1, B2, B3)

**Secondary:**
1. Positive correlation between IFEval improvement (from H-M2) and safety improvement
2. Consistent improvement direction across both benchmarks
3. Statistical significance (p < 0.05, bootstrap or paired t-test)

### Failure Analysis Protocol

**If gate fails (no Ti improves ≥2pp):**
1. Document as limitation: explicit→implicit transfer may not hold
2. Analyze per-category breakdown (which safety categories show movement?)
3. Correlate with IFEval constraint types (format vs content constraints)
4. Consider confound: TruthfulQA/BBQ may be saturated for 8B models

---

## Implementation Pseudo-code

### Main Evaluation Script

```python
"""
h-c1/code/evaluate_safety.py
Evaluates T1-T4 and baselines on TruthfulQA and BBQ
"""

import json
from pathlib import Path
from lm_eval import evaluator
from lm_eval.models.huggingface import HFLM

# Model checkpoints (from H-M2/H-M3)
MODELS = {
    "B1": "meta-llama/Meta-Llama-3-8B-Instruct",
    "B2": "../h-m2/code/checkpoints/b2_helpfulness_only",
    "B3": "../h-m2/code/checkpoints/b3_quality_only",
    "T1": "../h-m2/code/checkpoints/t1_alpha0.2_beta0.8",
    "T2": "../h-m2/code/checkpoints/t2_alpha0.4_beta0.6",
    "T3": "../h-m2/code/checkpoints/t3_alpha0.6_beta0.4",
    "T4": "../h-m2/code/checkpoints/t4_alpha0.8_beta0.2",
}

TASKS = ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]

def evaluate_model(model_name: str, checkpoint: str) -> dict:
    """Evaluate single model on safety benchmarks."""
    model = HFLM(pretrained=checkpoint)
    results = evaluator.simple_evaluate(
        model=model,
        tasks=TASKS,
        batch_size="auto:4"
    )
    return {
        "model": model_name,
        "truthfulqa_mc1": results["results"]["truthfulqa_mc1"]["acc"],
        "truthfulqa_mc2": results["results"]["truthfulqa_mc2"]["acc"],
        "bbq": results["results"]["bbq"]["acc"],
    }

def main():
    results = {}
    for name, checkpoint in MODELS.items():
        print(f"Evaluating {name}...")
        results[name] = evaluate_model(name, checkpoint)
    
    # Save results
    output_path = Path("outputs/safety_results.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # Compute gate condition
    baselines = [results["B1"], results["B2"], results["B3"]]
    max_truthful = max(b["truthfulqa_mc1"] for b in baselines)
    max_bbq = max(b["bbq"] for b in baselines)
    
    print("\n=== GATE EVALUATION ===")
    gate_passed = False
    for ti in ["T1", "T2", "T3", "T4"]:
        delta_truthful = results[ti]["truthfulqa_mc1"] - max_truthful
        delta_bbq = results[ti]["bbq"] - max_bbq
        print(f"{ti}: TruthfulQA Δ={delta_truthful:.2%}, BBQ Δ={delta_bbq:.2%}")
        if delta_truthful >= 0.02 or delta_bbq >= 0.02:
            gate_passed = True
            print(f"  → GATE PASS: ≥2pp improvement")
    
    print(f"\nOverall Gate: {'PASS' if gate_passed else 'FAIL'}")
    return gate_passed

if __name__ == "__main__":
    main()
```

### Statistical Analysis

```python
"""
h-c1/code/analyze_transfer.py
Analyze correlation between IFEval and safety improvements
"""

import json
import numpy as np
from scipy import stats

def analyze_transfer(safety_results: dict, ifeval_results: dict):
    """Correlate IFEval improvement with safety improvement."""
    
    treatments = ["T1", "T2", "T3", "T4"]
    
    # Get baseline max for each metric
    baselines = ["B1", "B2", "B3"]
    max_ifeval = max(ifeval_results[b]["strict_acc"] for b in baselines)
    max_truthful = max(safety_results[b]["truthfulqa_mc1"] for b in baselines)
    max_bbq = max(safety_results[b]["bbq"] for b in baselines)
    
    # Compute deltas for treatments
    ifeval_deltas = [ifeval_results[t]["strict_acc"] - max_ifeval for t in treatments]
    truthful_deltas = [safety_results[t]["truthfulqa_mc1"] - max_truthful for t in treatments]
    bbq_deltas = [safety_results[t]["bbq"] - max_bbq for t in treatments]
    
    # Correlation analysis
    r_truthful, p_truthful = stats.pearsonr(ifeval_deltas, truthful_deltas)
    r_bbq, p_bbq = stats.pearsonr(ifeval_deltas, bbq_deltas)
    
    print("=== TRANSFER CORRELATION ANALYSIS ===")
    print(f"IFEval ↔ TruthfulQA: r={r_truthful:.3f}, p={p_truthful:.4f}")
    print(f"IFEval ↔ BBQ: r={r_bbq:.3f}, p={p_bbq:.4f}")
    
    return {
        "correlation_truthfulqa": {"r": r_truthful, "p": p_truthful},
        "correlation_bbq": {"r": r_bbq, "p": p_bbq},
    }
```

---

## Metrics & Analysis Plan

### Primary Metrics

| Metric | Source | Gate Threshold |
|--------|--------|----------------|
| TruthfulQA MC1 | lm-eval-harness | ≥2pp over max(baselines) |
| TruthfulQA MC2 | lm-eval-harness | ≥2pp over max(baselines) |
| BBQ Accuracy | lm-eval-harness | ≥2pp over max(baselines) |

### Secondary Metrics

| Metric | Purpose |
|--------|---------|
| Per-category breakdown | Identify which safety categories improve |
| IFEval-Safety correlation | Test transfer mechanism hypothesis |
| Constraint type analysis | Which IFEval constraints predict safety gains |

### Expected Results

Based on H-M2/H-M3 findings:
- T2 (highest IFEval) most likely to show safety transfer
- T4 (highest helpfulness) may show smaller safety gains
- Positive correlation expected between IFEval Δ and safety Δ

### Reporting Template

```markdown
## H-C1 Results

### Gate Evaluation
| Model | TruthfulQA MC1 | TruthfulQA MC2 | BBQ | Gate |
|-------|----------------|----------------|-----|------|
| B1 | X% | X% | X% | — |
| B2 | X% | X% | X% | — |
| B3 | X% | X% | X% | — |
| T1 | X% (Δ+X) | X% (Δ+X) | X% (Δ+X) | PASS/FAIL |
| T2 | X% (Δ+X) | X% (Δ+X) | X% (Δ+X) | PASS/FAIL |
| T3 | X% (Δ+X) | X% (Δ+X) | X% (Δ+X) | PASS/FAIL |
| T4 | X% (Δ+X) | X% (Δ+X) | X% (Δ+X) | PASS/FAIL |

### Transfer Correlation
- IFEval → TruthfulQA: r=X.XX, p=X.XX
- IFEval → BBQ: r=X.XX, p=X.XX

### Conclusion
[PASS/FAIL]: [Explanation of explicit→implicit transfer finding]
```

---

## Resource Requirements

### Compute
- GPU: Single A100-80GB (inference only, no training)
- Time: ~2-4 hours for full evaluation suite
- Storage: ~50GB for model checkpoints access

### Dependencies
```
lm-evaluation-harness>=0.4.0
transformers>=4.40.0
torch>=2.0.0
scipy
numpy
```

### Checkpoints (from H-M2/H-M3)
- [ ] B1: meta-llama/Meta-Llama-3-8B-Instruct (HuggingFace)
- [ ] B2: h-m2/code/checkpoints/b2_helpfulness_only
- [ ] B3: h-m2/code/checkpoints/b3_quality_only
- [ ] T1-T4: h-m2/code/checkpoints/t{1-4}_alpha*_beta*

---

## Validation Checklist

### Pre-Implementation
- [ ] All model checkpoints accessible
- [ ] lm-evaluation-harness installed and configured
- [ ] TruthfulQA and BBQ tasks available in harness

### During Implementation
- [ ] All 7 models evaluated on both benchmarks
- [ ] Results saved to structured JSON
- [ ] No evaluation errors or timeouts

### Post-Implementation
- [ ] Gate condition checked (≥2pp improvement)
- [ ] Correlation analysis completed
- [ ] Results documented in 04_validation.md

---

## Appendix: Benchmark Details

### TruthfulQA Categories (38 total)
Health, Law, Finance, Politics, Psychology, Science, Technology, History, Geography, Culture, Religion, Philosophy, Ethics, Logic, Math, Language, Art, Music, Sports, Food, Travel, Fashion, Entertainment, Social Media, Education, Environment, Business, Economics, Government, Military, Crime, Paranormal, Conspiracy, Misconceptions, Fiction, Stereotypes, Indexical, Subjective

### BBQ Bias Categories (9 total)
Age, Disability status, Gender identity, Nationality, Physical appearance, Race/ethnicity, Religion, Sexual orientation, Socioeconomic status

---

**Document Version:** 1.0
**Last Updated:** 2026-08-28
**Status:** Ready for Phase 4 Implementation
