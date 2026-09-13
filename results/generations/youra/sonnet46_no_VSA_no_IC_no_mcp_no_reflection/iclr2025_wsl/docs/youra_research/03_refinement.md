# Hypothesis Refinement: H-GenGapEquiv-v1

**Generated:** 2026-08-31  
**Phase:** 2A → 2B  
**Gap:** Systematic Comparison of Equivariant vs. Non-Equivariant Encoders on Generalization Gap Prediction  
**Decision:** PROCEED TO PHASE 2B

---

## Core Hypothesis

**Permutation-equivariant weight encoders (DWS, NFT, GNN) show a disproportionately larger Spearman correlation improvement over flat MLP on generalization gap prediction (train_acc − test_acc at convergence) compared to their improvement on test accuracy prediction.**

This is the differential sensitivity claim: equivariance helps *more* when the prediction target is the harder, more distributed generalization gap signal than when it is the locally-predictable test accuracy.

---

## Why This Gap Exists

Every major weight-space encoder paper (Navon 2023/DWS, Zhou 2023/NFT, Kofinas 2024/GNN) evaluates exclusively on test accuracy prediction. Unterthiner's model zoo records both train and test accuracy, so generalization gap (their difference) is directly computable — but nobody has used it as a prediction target in a controlled encoder comparison.

The gap is not a minor oversight. Whether equivariance helps specifically for overfitting prediction vs. performance prediction is a question about *why* equivariant encoders work — and answering it links two previously disconnected literatures: weight-space symmetry and generalization theory.

---

## Mechanistic Explanation

**Why should equivariant encoders help more for generalization gap?**

1. Generalization gap at convergence (overfitting signal) is **distributed across the entire weight tensor** — no single neuron or layer localizes it. Predicting it requires integrating information across the whole network.

2. Permutation-equivariant encoders achieve invariance through **parameter sharing across neuron equivalence classes**. This architecturally forces the encoder to compute statistics averaged over all neurons in an equivalence class — i.e., distributed statistics.

3. Flat MLPs on sorted/canonicalized weights can be permutation-invariant at inference, but during training they remain free to **fit sorting-dependent spurious features**. These features may correlate with test accuracy (which depends on the actual parameter values at specific positions) but not with generalization gap (which depends on distributed weight geometry).

4. Cross-layer attention (NFT) captures **inter-layer weight co-variation**, which is specifically relevant for overfitting (e.g., layers that are simultaneously large in norm correlate with overfit behavior). DWS, which is intra-layer equivariant, may miss this signal.

**Theoretical grounding:** PAC-Bayes flatness, margin, and sharpness measures are all permutation-invariant — they don't change when neurons are relabeled. Equivariant encoders have a matching inductive bias and should therefore more naturally capture these quantities.

---

## Predictions

### P1 (Primary)
At least two of three equivariant encoders (DWS, NFT, GNN) show:

```
Δ = [Spearman(gap) − Spearman_flatMLP(gap)] − [Spearman(test_acc) − Spearman_flatMLP(test_acc)] > 0.02
```

*Practical significance threshold: 0.02 Spearman units.*

### P2 (Secondary)
NFT achieves higher Spearman on generalization gap than DWS by ≥ 0.01, while DWS achieves comparable or better Spearman on test accuracy. This would confirm that cross-layer attention specifically benefits overfitting prediction.

### P3 (Statistical)
Partial Spearman correlation of equivariant encoder predictions with generalization gap — after controlling for test accuracy — is significantly positive (p < 0.05) for at least one equivariant encoder. This tests whether equivariant encoders capture gap-specific information beyond what test accuracy encodes.

---

## Experimental Design

### Phase 1: Data Audit (mandatory pre-condition)
- Load Unterthiner metadata CSV
- Compute `Spearman(generalization_gap, −test_acc)`
- **Condition A1:** Must be < 0.95 in absolute value to proceed on Unterthiner zoo
- If A1 fails → use Schürholt PDFD zoo as primary venue

### Phase 2: Encoder Training
- **Dataset:** Unterthiner CIFAR-10 CNN zoo (~10,000 models)
- **Split:** 80/10/10 stratified by hyperparameter configuration
- **Encoders:** flat MLP, DWS, NFT, GNN
- **Targets:** test_acc and generalization_gap (trained separately)
- **Search budget:** 50 random trials per encoder per target (pre-specified, locked before any training)
- **Model selection:** Spearman on validation set

### Phase 3: Evaluation
- Report Spearman r and MSE for all encoder × target combinations
- Report partial Spearman (P3)
- Report sensitivity: mean ± std across top-5 configurations per encoder
- Test set never touched during tuning

### Phase 4: Cross-Zoo Validation
- Repeat evaluation on Schürholt PDFD zoo
- Tests generalizability of the effect across zoo characteristics

### Baselines
- Flat MLP (Unterthiner original)
- Eilertsen weight statistics (spectral norms, layer means)
- Complexity measures from Jiang et al. 2019 if available on zoo

---

## Novelty

| Contribution | Prior State | This Work |
|---|---|---|
| Weight encoder evaluation target | Test accuracy only | + Generalization gap |
| Target-dependent equivariance effect | Unknown | First controlled test |
| Inductive bias ↔ generalization measures | Disconnected | Linked via PAC-Bayes invariance argument |
| Cross-encoder comparison on gap | None | DWS vs. NFT vs. GNN vs. flat MLP |

---

## Key Assumptions and Risks

| Assumption | Check | Fallback |
|---|---|---|
| A1: Gap has independent variance from test_acc | Data audit pre-experiment | PDFD zoo |
| A2: 50-trial budget is sufficient for all encoders | Sensitivity analysis across top-5 | Extend budget if variance is high |
| A3: Unterthiner zoo is representative | Cross-zoo validation on PDFD | PDFD as co-primary |
| A4: NFT code compatible with small CNN architecture | Test before committing | Adapt or use transformer analog |

**Scope limitation:** Claims are restricted to convergence-regime overfitting in fixed-architecture model zoos. Do not generalize to training dynamics or architectural diversity beyond the tested zoos.

---

## Resources Required

| Resource | Status |
|---|---|
| Unterthiner zoo data | Public (Zenodo) |
| DWSNets code | Public (github.com/AvivNavon/DWSNets) |
| neural-graphs code | Public (Kofinas et al. repo) |
| NFT code | Public (Zhou et al. repo) |
| Compute | Single GPU, ~2-4 days |
| New benchmarks | None required |
| Human annotation | None required |

---

## Mandatory Pre-Conditions for Phase 2B

1. Run data audit and confirm A1 before writing Phase 2B plan
2. Pre-specify and lock hyperparameter search budget (50 trials) in Phase 2B plan
3. Include partial correlation analysis (P3) in evaluation specification
4. Confirm NFT code compatibility with small CNN weight tensors

---

## Persona Consensus

| Persona | Verdict | Key Condition |
|---|---|---|
| Dr. Nova (Novelty) | Strong Support | None |
| Prof. Vera (Rigor) | Conditional | Data audit + fixed budget + partial corr |
| Dr. Sage (Impact) | Strong Support | None |
| Prof. Pax (Feasibility) | Support | NFT compatibility check |
| Dr. Ally (Strengthening) | Strong Support | None |
| Prof. Rex (Stress-test) | Conditional | Scope claims to convergence; sensitivity analysis |

**Overall: PROCEED TO PHASE 2B** — all six personas support, two with conditions that are addressed in the experimental design above.
