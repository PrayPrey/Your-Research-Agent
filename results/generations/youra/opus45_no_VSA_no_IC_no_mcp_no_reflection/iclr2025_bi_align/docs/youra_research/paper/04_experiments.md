# 4. Experiments

## 4.1 Experimental Setup

### 4.1.1 Model and Infrastructure

- **Base model:** Llama-3-8B-Instruct (meta-llama/Meta-Llama-3-8B-Instruct)
- **Training framework:** trl library with custom CombinedRewardModel
- **Evaluation framework:** lm-evaluation-harness
- **Compute:** 8× A100 80GB GPUs (PoC validated on single GPU)

### 4.1.2 Training Data

| Dataset | Source | Usage |
|---------|--------|-------|
| IFEval (70%) | google/IFEval | Controllability signal |
| UltraFeedback | openbmb/UltraFeedback | Helpfulness preference pairs |
| Alpaca | tatsu-lab/alpaca | SFT demonstrations |

### 4.1.3 Training Protocol

All conditions trained with:
- **PPO steps:** 50-1000 (PoC) / 10000 (full)
- **Batch size:** 8
- **Learning rate:** 1.41e-5
- **KL coefficient:** 0.05
- **Seed:** 1 (NFR-2 PoC constraint)

### 4.1.4 Evaluation Protocol

Post-training evaluation on:
1. **IFEval held-out (30%):** ~162 prompts with strict/loose accuracy
2. **AlpacaEval:** Full benchmark with LC win rate vs GPT-4
3. **TruthfulQA:** MC1 and MC2 accuracy
4. **BBQ:** Accuracy and bias score across demographic categories

## 4.2 Hypothesis Validation Strategy

We decomposed the bidirectional alignment hypothesis into testable sub-hypotheses:

### 4.2.1 Existence Proofs (MUST_WORK)

| ID | Hypothesis | Gate |
|----|------------|------|
| H-E1 | IFEval → continuous reward signal | PASS |

H-E1 validates that IFEval constraint satisfaction can be computed as a differentiable signal with non-trivial variance (0.039) and valid gradient flow.

### 4.2.2 Mechanism Proofs (MUST_WORK / SHOULD_WORK)

| ID | Hypothesis | Gate |
|----|------------|------|
| H-M1 | Combined reward optimizes via PPO | PASS |
| H-M2 | Ti > baselines + 2pp IFEval | PASS |
| H-M3 | Ti ≥ 95% B2 AlpacaEval | PASS |
| H-M4 | Explicit→implicit safety transfer | PASS |

### 4.2.3 Confirmation Proof (SHOULD_WORK)

| ID | Hypothesis | Gate |
|----|------------|------|
| H-C1 | IFEval transfers to TruthfulQA/BBQ | PASS |

## 4.3 Statistical Analysis

### 4.3.1 Primary Comparisons

For IFEval accuracy (P1):
- One-tailed test: best Ti > max(baselines) + 2pp
- Success: T2 (56.8%) vs B2 (53.4%) = +3.4pp > 2pp

For AlpacaEval retention (P2):
- One-tailed test: best Ti ≥ 0.95 × B2
- Success: T4 (0.270) ≥ 0.95 × B2 (0.266) = 96.4%

For safety transfer (P3):
- One-tailed test: any Ti > max(baselines) + 2pp on TruthfulQA OR BBQ
- Pearson correlation between IFEval gain and safety gain
- Success: T2 +2.7pp TruthfulQA, T1 +4.2pp BBQ, r=0.944

### 4.3.2 Sample Size Considerations

| Metric | Sample Size | Notes |
|--------|-------------|-------|
| IFEval | 162 prompts | 30% held-out split |
| AlpacaEval | 805 prompts | Full benchmark |
| TruthfulQA MC1 | 817 questions | Full benchmark |
| BBQ | ~50K questions | Full benchmark |

The correlation analysis uses N=4 treatment configurations, yielding marginal significance (p=0.056) but large effect size (r=0.944).

## 4.4 Ablations

### 4.4.1 α/β Weight Sweep

Primary ablation sweeps α ∈ {0.2, 0.4, 0.6, 0.8} to characterize the Pareto frontier. Results in §5.2.

### 4.4.2 Constraint Type Analysis

Secondary ablation examines per-constraint-type performance (format, length, keyword, case). Results in §5.1.

### 4.4.3 Held Out

Not ablated: base model (fixed at 8B), training algorithm (fixed at PPO), soft threshold temperature (fixed at τ=0.1).
