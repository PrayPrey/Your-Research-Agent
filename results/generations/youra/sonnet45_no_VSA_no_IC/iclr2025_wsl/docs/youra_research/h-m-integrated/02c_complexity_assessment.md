# Complexity Assessment: h-m-integrated

**Hypothesis ID:** h-m-integrated  
**Date:** 2026-08-20  
**Assessment Level:** MODERATE-HIGH  

---

## 1. Complexity Dimensions

### 1.1 Data Complexity: MODERATE
- **Dataset:** ModelZooDataset (2,120 models, 4 architectures, 9 tasks)
- **Coverage:** 72.2% validated in h-e1 (PREREQUISITE MET)
- **Files:** 1.8 GB + 5.5 GB PyTorch files (manageable size)
- **Preprocessing:** Architecture-task pairing + normalization (straightforward)
- **Rating Justification:** Dataset exists, validated, requires minimal preprocessing. No data collection or labeling needed.

### 1.2 Model Architecture Complexity: HIGH
- **3-Level Hierarchical VAE:**
  - Level 1: Architecture-specific encoders (NFN/UNF) - 4 separate encoders
  - Level 2: Hierarchical pooling - custom layer-wise aggregation
  - Level 3: Transformer relational modeling - 6-layer Transformer with CLS token
- **Component Count:** 7 major neural network modules (4 encoders + pooling + transformer + decoder)
- **Parameter Count:** Estimated 50-100M parameters total
- **Rating Justification:** Multi-stage architecture with heterogeneous encoders. Higher complexity than standard VAE. Lower complexity than multi-modal diffusion models.

### 1.3 Training Complexity: HIGH
- **Multi-Objective Loss:**
  - Reconstruction loss (MSE)
  - KL divergence (beta-annealed)
  - Contrastive triplet loss (margin-based)
  - Task classification loss (cross-entropy)
- **Training Procedure:**
  - 200 epochs
  - 7 days on 2x V100 GPUs
  - Gradient clipping + beta annealing schedule
- **Hyperparameter Tuning Space:** 8 key hyperparameters (latent_dim, beta_kl, lambda_contrast, gamma_task, etc.)
- **Rating Justification:** Multi-objective optimization with 4 loss terms. Annealing schedule adds complexity. Moderate hyperparameter search space.

### 1.4 Evaluation Complexity: MODERATE
- **Primary Metrics:**
  - CKA similarity (well-defined, existing implementations)
  - WCSS bootstrap test (standard clustering metric)
- **Statistical Tests:**
  - t-test for WCSS comparison (straightforward)
  - Cohen's d effect size (standard metric)
- **Ablation Studies:** 2 ablations (architecture token removal, zero-shot transfer)
- **Rating Justification:** Metrics are standard and well-documented. Statistical tests are simple. Multiple ablations add moderate complexity.

### 1.5 Risk Complexity: MODERATE-HIGH
- **5 Identified Risks:** R1 (coverage), R2 (noisy labels), R3 (information loss), R4 (training confound), R5 (subspace incompatibility)
- **Gated Risks:** 2 MUST_WORK gates (CKA feasibility, WCSS test)
- **Early Stop Opportunities:** Week 2 (CKA gate), Week 5 (WCSS gate)
- **Rating Justification:** Multiple failure modes, but all have clear detection criteria and mitigation strategies. Gates reduce wasted compute.

---

## 2. Implementation Complexity Score

### Scoring Rubric (1-5 scale)
1. **TRIVIAL:** Single-file script, <100 LOC, <1 day
2. **LOW:** 2-3 files, standard libraries, <3 days
3. **MODERATE:** 5-10 files, custom modules, 1-2 weeks
4. **HIGH:** 10+ files, complex architecture, multi-week project
5. **VERY HIGH:** Multi-repo integration, novel techniques, multi-month project

### h-m-integrated Score: **4.0 (HIGH)**

**Breakdown:**
- **File Count:** 12+ files (data/, models/, training/, evaluation/, notebooks/)
- **Custom Code:** 7 neural network modules (NFN encoder, pooling, transformer, baselines)
- **External Dependencies:** CKA libraries, NFN reference code, contrastive loss implementations
- **Timeline:** 6 weeks (11 GPU days)
- **Lines of Code (Estimated):** 2,000-3,000 LOC

**Justification:**
- 3-level hierarchical architecture requires significant custom code
- Multi-objective loss function adds training complexity
- Multiple evaluation phases with statistical tests
- Manageable within 6 weeks, but not a simple extension of existing code

---

## 3. Resource Requirements

### 3.1 Compute Resources
| Phase | GPU Type | GPU Hours | Storage | Estimated Cost |
|-------|----------|-----------|---------|----------------|
| Phase 1 (CKA Gate) | 1x V100 | 48 | 10 GB | $50 |
| Phase 2-3 (VAE Training) | 2x V100 | 336 | 50 GB | $700 |
| Phase 4 (Validation) | 1x V100 | 48 | 5 GB | $50 |
| **Total** | - | **432** | **65 GB** | **$800** |

**Resource Availability:** FEASIBLE (standard cloud GPU instances)

### 3.2 Human Resources
| Role | Effort (Person-Weeks) | Tasks |
|------|----------------------|-------|
| ML Engineer | 4 weeks | Architecture implementation, training loop |
| Research Scientist | 2 weeks | Experiment design, statistical analysis |
| Infrastructure | 1 week | Data pipeline, compute setup |
| **Total** | **5-6 weeks** | - |

**Team Size:** 1-2 people (ML engineer can handle infrastructure, research scientist can assist with implementation)

### 3.3 External Dependencies
- **NFN Reference Code:** https://github.com/AllanYangZhou/nfn (permutation-equivariant layers)
- **CKA Libraries:** https://github.com/numpee/CKA.pytorch (GPU-accelerated HSIC)
- **Contrastive Learning:** https://github.com/lucidrains/DALLE2-pytorch (triplet loss)
- **ModelZooDataset:** https://doi.org/10.5281/zenodo.6620868 (preprocessed data)

**Dependency Risk:** LOW (all repos are public, active, well-documented)

---

## 4. Complexity-Mitigating Factors

### 4.1 Prerequisite Validation (h-e1)
- **Coverage audit already completed:** 72.2% cells with ≥30 models
- **Critical cells identified:** CNN-CIFAR10 (250 models), ResNet-CIFAR100 (200 models)
- **Risk R1 (insufficient coverage) MITIGATED:** No additional dataset collection needed

### 4.2 Gated Execution
- **Phase 1 CKA Gate (Week 2):** Early stop if architecture subspaces incompatible
  - Saves 4 weeks of VAE training if fails
  - GPU cost savings: $700 (87.5% of total budget)
- **Phase 4 WCSS Gate (Week 5):** Early stop if clustering fails
  - Saves 1 week of ablation work
  - Documented failure enables Phase 2A pivot

### 4.3 Baseline Simplicity
- **Baseline 1 (ArchConditionedMLP):** Simple MLP, no custom architecture
- **Baseline 2 (NFN-only):** Single-architecture VAE, reuses NFN code
- **Baseline 3 (CKA Direct):** No learned model, direct metric computation

**Baseline Timeline:** 1 week (parallel with Phase 1 CKA gate)

### 4.4 Modular Architecture
- **Level 1 (Encoders):** Can test independently per architecture
- **Level 2 (Pooling):** Can validate reconstruction accuracy in isolation
- **Level 3 (Transformer):** Can ablate entirely if pooling sufficient (Scenario 3 failure case)

**Modularity Benefit:** Each level can be debugged/validated separately, reducing integration complexity

---

## 5. Complexity Comparison (Relative to Other Hypotheses)

### Hypothetical Benchmarks
| Hypothesis Type | Typical Complexity | h-m-integrated Complexity | Delta |
|----------------|-------------------|---------------------------|-------|
| Data-Driven Hypothesis (e.g., "Does X correlate with Y?") | LOW (2.0) | HIGH (4.0) | +2.0 |
| Single-Model Training (e.g., "Does architecture A outperform B?") | MODERATE (3.0) | HIGH (4.0) | +1.0 |
| Multi-Stage Pipeline (e.g., "Hierarchical VAE with gates") | HIGH (4.0) | HIGH (4.0) | 0.0 |
| Novel Architecture (e.g., "New transformer variant") | VERY HIGH (4.5) | HIGH (4.0) | -0.5 |

**Interpretation:** h-m-integrated is at the upper end of MODERATE-HIGH complexity. Higher than single-model training, but lower than novel architecture development.

---

## 6. Complexity Risks

### 6.1 Integration Complexity
- **Risk:** 7 separate modules (encoders, pooling, transformer, decoder) may have API mismatches
- **Mitigation:** Define clear interfaces early (e.g., all encoders output `(batch, num_neurons, dim)`)
- **Severity:** MEDIUM (can delay implementation by 1-2 weeks)

### 6.2 Training Instability
- **Risk:** Multi-objective loss may cause unstable gradients or loss conflicts
- **Mitigation:** Gradient clipping (1.0), beta annealing, separate learning rates per loss term
- **Severity:** MEDIUM (may require hyperparameter search, extend training by 1-2 weeks)

### 6.3 Hyperparameter Sensitivity
- **Risk:** 8 hyperparameters (latent_dim, beta_kl, lambda_contrast, etc.) may interact nonlinearly
- **Mitigation:** Phase 1 CKA gate validates feasibility before expensive hyperparameter search
- **Severity:** MEDIUM (may extend Phase 2-3 by 1 week)

### 6.4 Dependency Versioning
- **Risk:** NFN code uses PyTorch 1.x, ModelZooDataset uses PyTorch 2.x
- **Mitigation:** Create isolated virtual environment, pin dependency versions in `requirements.txt`
- **Severity:** LOW (1-2 days to resolve version conflicts)

---

## 7. Complexity Reduction Opportunities

### 7.1 Simplify Level 3 (Transformer → Simple Attention)
- **Current:** 6-layer Transformer with 8 heads (large parameter count)
- **Alternative:** 2-layer Transformer OR single-head attention pooling
- **Impact:** Reduces parameters by 60%, training time by 30%
- **Risk:** May reduce relational modeling capacity (test via ablation in Phase 4)

### 7.2 Reduce Architecture Coverage (4 → 2 Architectures)
- **Current:** CNN-small, CNN-large, ResNet-18, ResNet-34 (4 encoders)
- **Alternative:** CNN-small + ResNet-18 only (2 encoders)
- **Impact:** Reduces encoder implementation by 50%, simpler debugging
- **Risk:** May not generalize to full heterogeneous zoo (limits scientific claims)

### 7.3 Use Pre-Trained Encoders (Transfer Learning)
- **Current:** Train NFN/UNF encoders from scratch
- **Alternative:** Use pre-trained NFN from AllanYangZhou/nfn, fine-tune on ModelZooDataset
- **Impact:** Reduces Phase 1 from 2 weeks to 3-5 days
- **Risk:** Pre-trained encoders may not align with task-specific patterns

---

## 8. Recommended Complexity Level

### Final Assessment: **PROCEED AT MODERATE-HIGH COMPLEXITY**

**Rationale:**
1. **Prerequisite Validated (h-e1):** Dataset coverage already confirmed, reduces data risk
2. **Gated Execution:** Early stop opportunities prevent wasted compute
3. **Modular Design:** Each level can be validated independently
4. **Standard Components:** Most modules have reference implementations (NFN, CKA, contrastive loss)
5. **Feasible Timeline:** 6 weeks with clear milestones and gates

**Recommendation:**
- **DO NOT SIMPLIFY** unless Phase 1 CKA gate fails
- **Monitor** integration complexity in Week 1-2
- **Pivot** to simplified architecture (e.g., 2-layer Transformer) if training instability in Week 3-4
- **Abort** if Phase 4 WCSS gate fails (documented failure is valuable scientific outcome)

---

## 9. Complexity Decision Tree

```
START: h-m-integrated complexity assessment

IF h-e1 coverage < 60%:
  → ABORT (Risk R1 not mitigated)
ELSE:
  → PROCEED TO PHASE 1

WEEK 2 (CKA Gate):
  IF same-task CKA < 0.5 OR diff-task CKA > 0.5:
    → ABORT Phase 2-3
    → PIVOT: Test nonlinear alignment (RBF kernel) OR scope to homogeneous subsets
  ELSE:
    → PROCEED TO PHASE 2-3

WEEK 4 (VAE Training):
  IF training instability (loss oscillates >50% for 10 epochs):
    → SIMPLIFY: Reduce Transformer to 2 layers
    → Extend timeline by 1 week
  ELSE:
    → PROCEED TO PHASE 4

WEEK 5 (WCSS Gate):
  IF p-value > 0.01 OR Cohen's d < 0.3:
    → ABORT (documented failure)
    → RETURN TO PHASE 2A: Explore alternative mechanisms
  ELSE:
    → PROCEED TO PHASE 4 ABLATIONS

WEEK 6 (Ablations):
  IF ablation degradation < 5%:
    → SIMPLIFY: Remove Transformer (Level 3), retest with pooling-only
    → Document simplification opportunity
  ELSE:
    → SUCCESS: Full 3-level VAE validated
```

---

## 10. Conclusion

**h-m-integrated is FEASIBLE at MODERATE-HIGH complexity.**

**Key Success Factors:**
- Prerequisite h-e1 mitigates dataset risk
- Gated execution prevents runaway compute costs
- Modular architecture enables incremental validation
- Reference implementations available for most components

**Key Risk Factors:**
- Multi-objective training may be unstable
- 7 modules create integration complexity
- Hyperparameter sensitivity may extend timeline

**Go/No-Go Decision:** **GO**  
Proceed with full 6-week implementation plan. Monitor CKA gate (Week 2) and WCSS gate (Week 5) for early stop triggers.
