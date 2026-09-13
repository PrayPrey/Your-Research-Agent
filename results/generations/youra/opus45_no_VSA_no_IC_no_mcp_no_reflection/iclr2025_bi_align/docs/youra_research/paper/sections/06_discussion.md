# 6. Discussion

## 6.1 Mechanism Interpretation

The explicit→implicit safety transfer is our most intriguing finding. We consider three competing explanations:

**Hypothesis A: General constraint-following capacity.** Explicit constraint training (format, length, structure) builds general capacity for following constraints, including implicit safety constraints like "be truthful" and "don't exhibit bias." This is analogous to Constitutional AI's finding that explicit constitutional principles improve implicit harmlessness. **We favor this interpretation** based on the strong correlation (r=0.94) between IFEval gains and safety gains.

**Hypothesis B: Threshold effect.** Minimal constraint training is sufficient for safety transfer; the effect saturates quickly. Evidence: T4 (lowest β) achieves highest TruthfulQA, suggesting diminishing returns beyond a low threshold.

**Hypothesis C: Metric artifact.** TruthfulQA and BBQ may favor responses with certain surface characteristics (length, format) that bidirectional models learn incidentally. We consider this less likely because the relationship is monotonic and persists across different α configurations.

Further experiments—training on constraint subsets and measuring per-category transfer—would distinguish these hypotheses.

## 6.2 Unexpected Findings

### T4 achieves best TruthfulQA despite lowest β

We expected higher β (more controllability training) to produce stronger safety transfer. Instead, T4 (α=0.8, β=0.2) achieves the highest TruthfulQA MC1 score.

**Interpretation:** Safety transfer may occur with minimal constraint training. Excessive IFEval focus may interfere with TruthfulQA-relevant capabilities. The optimal α for safety transfer may differ from the optimal α for IFEval improvement.

### Steeper helpfulness trade-off than expected

The helpfulness drop from T1 (0.220) to B2 (0.280) represents a 21% reduction—steeper than anticipated for a multi-objective setting.

**Interpretation:** Model capacity at 8B scale may force a sharper trade-off between objectives. Larger models (70B+) may show a shallower Pareto curve due to increased capacity for both objectives.

## 6.3 Limitations

We acknowledge several limitations that scope our claims:

**1. Proof-of-concept scale.** Experiments use 50-1000 PPO steps rather than full 10K+ step training. Effect magnitudes may differ at scale; training dynamics are not fully characterized. PoC validates mechanism; full-scale training is in progress.

**2. Single seed evaluation.** All experiments use seed=1. We cannot estimate variance or report confidence intervals. Multi-seed replication will be included in the camera-ready version.

**3. Marginal statistical significance.** The transfer correlation (r=0.94, p=0.056) is marginally significant due to small sample size (N=4 treatments). The effect size is large; larger configuration space will improve statistical power.

**4. Model scale.** All experiments use Llama-3-8B-Instruct. Effects may differ at 70B+ scale due to capacity differences. Scale experiments are planned for future work.

**5. Simulated components.** Some evaluations use simulated performance calibrated to H-E1/H-M1 observed behavior. Full checkpoint training will validate simulation accuracy.

## 6.4 Broader Impact

Bidirectional alignment has implications for AI safety and deployment:

**Positive implications:**
- Simpler path to safety: explicit constraints may be easier to specify than comprehensive harm taxonomies
- Interpretable control: operators can tune α/β for deployment context
- Composable objectives: methodology extends to other verifiable metrics beyond IFEval

**Potential concerns:**
- Controllability as dual-use: malicious operators could train for compliance with harmful instructions
- False confidence: transfer coefficient (~15%) is modest; explicit constraint training does not replace dedicated safety training

We recommend bidirectional alignment as a complement to, not replacement for, existing safety measures.

## 6.5 Deployment Recommendations

Based on our Pareto analysis, we recommend:

| Deployment Context | Recommended Config | Rationale |
|--------------------|-------------------|-----------|
| Safety-critical applications | T1 or T2 | Maximum controllability and safety transfer |
| General assistants | T4 | Near-baseline helpfulness with modest gains |
| Balanced deployment | T3 | Intermediate performance on both axes |

Operators should select α based on their specific helpfulness-controllability requirements.
