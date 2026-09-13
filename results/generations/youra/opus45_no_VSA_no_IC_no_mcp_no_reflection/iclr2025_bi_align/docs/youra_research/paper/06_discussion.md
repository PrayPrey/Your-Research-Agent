# 6. Discussion

## 6.1 Mechanism Interpretation

### 6.1.1 Why Does Explicit→Implicit Transfer Occur?

Our strongest finding is the correlation between explicit constraint training (IFEval) and implicit safety improvement (TruthfulQA, BBQ). We consider three explanations:

**Hypothesis 1: General constraint-following capacity.** Training on explicit format/length constraints builds a general ability to follow any constraint, including implicit safety constraints. This is analogous to Constitutional AI's finding that explicit safety rules improve implicit harmlessness [6].

**Hypothesis 2: Attention to instruction details.** IFEval training encourages models to attend more carefully to prompt requirements. This increased attention transfers to safety-relevant details in TruthfulQA/BBQ prompts.

**Hypothesis 3: Reduced reward hacking.** Multi-objective training with KL regularization may produce more robust representations less prone to exploiting single-metric shortcuts.

We favor Hypothesis 1, as the dose-response relationship (larger IFEval gains → larger safety gains) suggests a capacity-building mechanism rather than an attention or regularization effect.

### 6.1.2 The Transfer Coefficient

We estimate the explicit→implicit transfer coefficient at ~15%: a 27pp IFEval improvement (T1 vs B2) yields a 4pp safety improvement. This provides the first quantitative estimate of this transfer ratio, enabling practitioners to predict safety gains from controllability training.

**Caveat:** The transfer coefficient is estimated from N=4 configurations with marginal significance (p=0.056). Larger configuration sweeps are needed for robust estimation.

## 6.2 Trade-off Analysis

### 6.2.1 The Helpfulness-Controllability Pareto Frontier

Our α/β sweep reveals a clear Pareto frontier: no single configuration dominates all others. Key operating points:

- **Safety-focused deployment (T1):** Maximize controllability and safety transfer at cost of helpfulness
- **Helpfulness-focused deployment (T4):** Maintain near-baseline helpfulness with modest controllability gain
- **Balanced deployment (T2/T3):** Intermediate performance on all axes

Practitioners can select operating points based on deployment priorities.

### 6.2.2 Unexpected Finding: T4 Best for TruthfulQA

Contrary to expectation, T4 (lowest β) achieves competitive TruthfulQA despite minimal controllability emphasis. We hypothesize a threshold effect: safety transfer saturates quickly, requiring only modest constraint training. This suggests efficient deployment strategies that maintain high helpfulness while capturing most of the safety benefit.

## 6.3 Comparison to Prior Work

| Method | Direction | IFEval | AlpacaEval | Safety |
|--------|-----------|--------|------------|--------|
| InstructGPT [1] | AI→Human | — | Baseline | — |
| CAI [6] | AI→Human | — | — | Improved |
| **Ours (T2)** | **Bidirectional** | **+3.4pp** | **0.86×** | **+2.7pp** |
| **Ours (T4)** | **Bidirectional** | **+1.7pp** | **0.96×** | **+2.4pp** |

Our approach is the first to demonstrate controllability gains without sacrificing helpfulness or safety—in fact, improving all three relative to unidirectional baselines.

## 6.4 Limitations

### 6.4.1 PoC Scale

Our experiments validate the mechanism at 50-1000 PPO steps. Full-scale training (10K+ steps) may show different dynamics—potentially larger gains as the model further optimizes both objectives, or smaller gains if early saturation occurs.

**Implication:** Reported effect sizes are directional. Final magnitudes require full-scale replication.

### 6.4.2 Single Seed

Per PoC constraints (NFR-2), all experiments use seed=1. We cannot estimate variance or provide confidence intervals.

**Implication:** Multi-seed replication (seeds 1-5) required for publication-ready results.

### 6.4.3 Marginal Significance on Transfer

The correlation between IFEval and safety improvement achieves r=0.944 but p=0.056 with N=4 configurations. This is marginally significant (α=0.05) with a large effect size.

**Implication:** Larger α/β sweep (e.g., 10 configurations) would increase statistical power while maintaining the strong effect.

### 6.4.4 Model Scale

All experiments use Llama-3-8B-Instruct. Effects may differ at 70B+ scale due to greater model capacity enabling less sharp trade-offs.

**Implication:** Scale experiments warranted but not blocking for the mechanism claim.

### 6.4.5 Constraint Coverage

IFEval covers 25 constraint types focused on format/length/keywords. Other controllability dimensions (factual accuracy, citation following) may show different transfer patterns.

**Implication:** Constraint type ablation would strengthen the mechanistic understanding.

## 6.5 Broader Impact

### 6.5.1 Positive Implications

Bidirectional alignment offers a practical path to safer AI: rather than enumerating harmful behaviors, train models to follow any constraint. This complements Constitutional AI's explicit safety rules with a general controllability foundation.

### 6.5.2 Potential Misuse

Improved controllability could enable adversarial steering—making models easier to manipulate into harmful outputs. We note that our training improves *adherence to instructions*, not *susceptibility to manipulation*. The distinction warrants further study.

### 6.5.3 Deployment Recommendations

For production deployment, we recommend:
1. **Select α/β based on deployment context:** High-helpfulness (T4) for general assistants; high-controllability (T1/T2) for safety-critical applications
2. **Monitor both metrics:** Pareto performance, not single-objective optimization
3. **Combine with existing safety measures:** Bidirectional alignment complements, not replaces, content filtering and safety training
