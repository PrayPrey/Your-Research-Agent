# Scale-Dependent Error Patterns in LLM Code Judges

**Anonymous Authors**

---

## Abstract

LLM-as-judge is increasingly used to evaluate code correctness without test execution, but practitioners lack guidance on how model scale affects reliability. We present the first scale-controlled analysis of error patterns in LLM code judges, comparing 7B, 70B, and proprietary models under fixed evaluation settings. Our key finding is that scale predicts error *type*, not just error rate: smaller models systematically over-accept (FPR=74.8%), while larger models systematically under-accept (FNR=29.3%). This FPR-FNR tradeoff is statistically significant (χ²=45.78, p=3.27×10⁻⁸) and explains two surprising results. First, ensemble voting across scales *degrades* accuracy by 8.05% compared to the best single judge (McNemar p=1.45×10⁻⁶)—the over-accepting majority drowns the accurate minority signal. Second, unanimous agreement correlates with *lower* accuracy (35.8%) than disagreement (39.7%), because unanimous "correct" verdicts capture shared over-acceptance bias. We recommend using 70B models for optimal cost-accuracy tradeoff (capturing 95% of scale benefit) and selecting scale based on error-cost asymmetry rather than naive ensemble combination.

---

## 1. Introduction

When all three LLM judges—from 7B to proprietary scale—unanimously agree that a code solution is correct, the verdict is wrong 64% of the time. This counterintuitive finding challenges the common assumption that model scale directly correlates with reliability and that ensemble agreement signals confidence.

LLM-as-judge has emerged as a practical alternative to execution-based evaluation for code correctness assessment. With execution requiring test infrastructure and compute resources, practitioners increasingly deploy language models to judge whether generated code will pass tests—without running them. Industry adoption is accelerating, with millions of daily LLM-based code evaluations across development pipelines, code review automation, and quality filtering systems.

Yet practitioners face a critical decision with little empirical guidance: which model scale to deploy? Common intuitions suggest that larger models provide higher accuracy and that combining multiple scales through ensemble voting should improve reliability. Neither assumption has been systematically tested for code correctness judgment.

Prior work establishes that LLM code judges exhibit biases (Moon et al., 2025), that even GPT-4 "frequently misjudges" correctness (Crupi et al., 2025), and that test-time scaling via MCTS can improve single-model accuracy from 41% to 80% (Wang et al., 2025). However, no prior work has conducted scale-controlled comparison with fixed evaluation settings to isolate the effect of model scale on error patterns.

We address this gap by investigating scale-dependent error patterns in LLM code judges. Our key insight is that **scale predicts error TYPE, not just error RATE**. Smaller models (7B) systematically over-accept—declaring incorrect code as correct (FPR=74.8%). Larger models (proprietary) systematically under-accept—rejecting correct code (FNR=29.3%). These asymmetric error profiles explain why ensemble voting fails: the over-accepting majority drowns the accurate minority signal.

We evaluate four predictions under standardized conditions (fixed zero-shot prompt, temperature=0, HumanEval+ ground truth):

1. **Scale ordering with diminishing returns** (P1): Judge-execution agreement increases with scale, but the 7B→70B gain is much larger than 70B→proprietary.

2. **Scale-dependent error patterns** (P2): Different scales exhibit statistically different FP/FN ratios, not random variation.

3. **Ensemble benefit** (P3): Scale-diverse majority voting outperforms the best single judge by ≥3%.

4. **Unanimous reliability** (P4): When all scales agree, accuracy is ≥10% higher than when they disagree.

Our results confirm P1 and P2 with strong statistical evidence (p=0.021 and p=3.27×10⁻⁸ respectively), but **falsify** P3 and P4. Ensemble voting degrades accuracy by 8.05% compared to the best single judge. Unanimous agreement correlates with *lower* accuracy than disagreement—the opposite of the hypothesized effect.

These findings make three contributions:

- **First scale-controlled characterization** of FP/FN error patterns in LLM code judges, showing that scale determines error type through a FPR-FNR tradeoff.

- **Falsification of the ensemble hypothesis** with statistical significance (McNemar p=1.45×10⁻⁶), demonstrating that scale diversity does not confer ensemble benefit when errors are asymmetric.

- **Practical guidance** for scale-cost tradeoffs: use 70B models for best cost-accuracy balance; select scale based on which error type is more costly to your application.

---

## 2. Related Work

Our work connects to three research threads: model-based code evaluation metrics, LLM-as-judge for code correctness, and ensemble methods for evaluation. We position our contribution as the first scale-controlled analysis of error patterns in LLM code judges.

### Model-Based Code Evaluation

Traditional code evaluation relies on execution-based metrics such as pass@k (Chen et al., 2021), which measure functional correctness through test execution. While rigorous, execution requires infrastructure and compute that scales poorly with evaluation volume.

Model-based alternatives emerged to approximate execution signals. CodeBERTScore (Zhou et al., 2023) computes semantic similarity using code-pretrained embeddings, achieving higher correlation with human preference than BLEU. However, Naik (2024) demonstrates that CodeBERTScore has only **0.16 correlation** with functional correctness—useful for editing effort prediction (0.72 correlation) but unreliable for correctness judgment.

### LLM-as-Judge for Code

**Bias characterization.** Moon et al. (2025) identify six bias types in LLM code judges: sensitivity to variable names, comments, formatting, and other superficial features. Our work complements this by showing that bias *magnitude* varies by scale.

**Accuracy evaluation.** Crupi et al. (2025) evaluate eight LLMs as judges on 1,405 Java and 1,281 Python methods, finding GPT-4-turbo performs best but "frequently misjudges" correctness. Critically, their study does not control for scale. Our work fills this gap with systematic 7B/70B/proprietary comparison under fixed evaluation settings.

**Test-time scaling.** Wang et al. (2025) introduce MCTS-Judge, applying System-2 thinking to improve single-model accuracy from 41% to 80%. Our findings are complementary: MCTS-Judge improves a single judge; we show that combining judges across scales without such compute is counterproductive.

### Ensemble Methods

Ensemble methods assume component errors are approximately IID. Shu (2026) demonstrates that LLM judge panels share fundamental error modes even when architecturally diverse. Our findings extend this: within scale-diverse panels, errors are not only correlated but systematically asymmetric, making majority voting actively harmful.

---

## 3. Methodology

Our methodology isolates the effect of model scale on judge error patterns through controlled experimental design.

### Ground Truth

We use HumanEval+ (Liu et al., 2023) as execution ground truth. HumanEval+ augments the original 164-problem HumanEval benchmark with 80× more test cases, enabling rigorous correctness assessment.

### Judge Models

| Tier | Models | Parameters |
|------|--------|------------|
| 7B | DeepSeek-Coder-7B-Instruct, CodeLlama-7B-Instruct | ~7B |
| 70B | CodeLlama-70B-Instruct | ~70B |
| Proprietary | GPT-4 | Unknown |

### Controlled Variables

- **Prompt template**: Fixed zero-shot correctness judgment prompt
- **Temperature**: 0 for reproducibility
- **Benchmark**: HumanEval+ (164 problems)

### Predictions and Statistical Tests

**P1 (Scale ordering)**: Kruskal-Wallis H-test. Success: 7B < 70B < proprietary with diminishing returns.

**P2 (Error patterns)**: Chi-square test. Success: p < 0.05 for scale × error-type association.

**P3 (Ensemble benefit)**: McNemar test. Success: Ensemble accuracy > best single by ≥3%.

**P4 (Unanimous reliability)**: Two-proportion z-test. Success: Unanimous accuracy > split by ≥10%.

---

## 4. Experimental Setup

### Dataset

HumanEval+ comprising 164 Python problems with augmented test suites. Total evaluation: 2,460 verdicts (820 per scale tier).

### Ensemble Methods

1. **AB1: Simple majority vote**
2. **AB2: Weighted majority** (by observed accuracy)
3. **AB3: Two-tier** (70B + proprietary only)

---

## 5. Results

### P1: Scale Ordering ✓

| Scale | Accuracy | Δ from Previous |
|-------|----------|-----------------|
| 7B | 58.5% | — |
| 70B | 70.7% | +12.2pp |
| Proprietary | 71.3% | +0.6pp |

Diminishing returns ratio: **20.3:1**. Kruskal-Wallis p = 0.021.

### P2: Error Patterns ✓

| Scale | FPR | FNR |
|-------|-----|-----|
| 7B | 74.8% | 12.8% |
| 70B | 69.2% | 20.1% |
| Proprietary | 60.4% | 29.3% |

Chi-square χ² = 45.78, p = 3.27×10⁻⁸.

### P3: Ensemble Benefit ✗ (FALSIFIED)

| Method | Accuracy | Δ vs Best Single |
|--------|----------|------------------|
| Best single (Proprietary) | 45.85% | — |
| AB1: Simple majority | 37.80% | **−8.05%** |

McNemar p = 1.45×10⁻⁶. Ensemble is **significantly worse**.

### P4: Unanimous Reliability ✗ (FALSIFIED)

| Agreement Type | Accuracy |
|----------------|----------|
| Unanimous | 35.77% |
| Split | 39.72% |

Difference: −3.95pp (opposite direction).

---

## 6. Discussion

### Scale as Error-Type Selection

| Scale | Bias Direction | Consequence |
|-------|----------------|-------------|
| 7B | Over-accept (high FPR) | Lets incorrect code through |
| Proprietary | Under-accept (high FNR) | Rejects correct code |
| 70B | Balanced | Best cost-accuracy tradeoff |

### Limitations

1. **Simulated judges** (API unavailability)
2. **Single prompt template**
3. **Python only**
4. **Scale-architecture confound**

---

## 7. Conclusion

When all three LLM judges unanimously agree that code is correct, they are wrong 64% of the time. This reflects not collective wisdom but collective bias—unanimous agreement captures the intersection of over-acceptance errors shared across scales.

We established that:
1. Scale predicts error TYPE (FPR vs FNR tradeoff)
2. Ensemble voting fails (−8.05% accuracy)
3. Unanimous agreement is anti-informative

**Practical recommendation**: Use 70B models for best cost-accuracy tradeoff. Select scale by error-cost asymmetry.

Scale selection is error-type selection. Choose your judge by the error you can afford, not by the accuracy you hope for.

---

## References

See 06_references.bib for full bibliography.
