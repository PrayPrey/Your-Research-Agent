# Product Requirements Document: H-M3

**Hypothesis:** Token-level achieves superior F1 retention at extrapolated lengths with significant interaction effect
**Type:** MECHANISM
**Date:** 2026-08-18
**Author:** YouRA Research Pipeline

---

## 1. Executive Summary

This experiment tests whether the representation stability advantage of token-level distillation (CAB) over matrix-level distillation (MOHAWK) demonstrated in H-M2 translates to superior downstream task performance at extrapolated sequence lengths. We evaluate both distillation objectives across a 2×3 factorial design on LongBench QA tasks.

**Success Criteria:** 
- Interaction term (Objective × Length) significant at p<0.05
- P2: CAB > MOHAWK by ≥3 F1 points at 16K
- P3: CAB > MOHAWK by ≥5 F1 points at 32K

---

## 2. Problem Statement

### 2.1 Context
H-M2 validated that CAB drift slope is 5× lower than MOHAWK (0.00090506 vs 0.00452495), demonstrating more stable hidden state representations across sequence lengths. This establishes the mechanistic basis for testing downstream performance.

### 2.2 Research Question
Does token-level distillation's representation stability advantage translate to measurably superior F1 retention on QA benchmarks at extrapolated lengths (16K, 32K)?

### 2.3 Hypothesis
Token-level (CAB) achieves superior F1 retention at extrapolated lengths, with the advantage growing as sequence length increases (interaction effect). At training-distribution lengths (4K), both objectives perform comparably.

---

## 3. Functional Requirements

### FR-1: Model Training Pipeline (6 Conditions)
- Train 6 model variants: 2 objectives × 3 lengths (4K/16K/32K)
- MOHAWK: Matrix-level MSE loss on attention maps
- CAB: Token-level Q/K→B/C alignment via MLP bridge
- Training: 1.5B tokens per condition on C4
- Hardware: 8× A100 80GB (4 weeks estimated)

### FR-2: Data Loading Pipeline
- Load LongBench QA tasks from THUDM/LongBench (HuggingFace)
- Tasks: narrativeqa, qasper, multifieldqa_en, hotpotqa, 2wikimqa, musique, triviaqa
- Use full test splits (~200 samples per task × 7 tasks = ~1400 samples total)
- Create length buckets: 4K, 16K, 32K via truncation strategy

### FR-3: Teacher and Student Model Loading
- **Teacher:** microsoft/phi-1_5 (reference F1 baseline)
- **MOHAWK Students:** Train or load phi-mamba variants at each length
- **CAB Students:** Train CAB variants with AttentionBridge at each length

### FR-4: CAB Implementation (from H-M2 continuation)
- AttentionBridge MLP: Q→B and K→C projection
- Token-level MSE loss on B/C projections
- Hierarchical layer alignment strategy

### FR-5: F1 Evaluation
- Generate responses for each LongBench QA sample
- Compute token-level F1 using LongBench's qa_f1_score
- Aggregate per-task and per-length bucket

### FR-6: Statistical Analysis
- 2×3 ANOVA: Factor A (Objective), Factor B (Length), A×B Interaction
- Per-length t-tests for P2/P3 effect size verification
- 95% confidence intervals on all effect estimates

### FR-7: Visualization
- **Required:** F1 Retention bar chart by condition (X: length, bars: MOHAWK/CAB)
- **Required:** Interaction plot (lines cross between 4K-16K)
- **Optional:** Per-task breakdown, effect size heatmap

---

## 4. Data Specification

### 4.1 Training Dataset

| Attribute | Value |
|-----------|-------|
| Name | C4 (Colossal Clean Crawled Corpus) |
| Source | allenai/c4 (HuggingFace) |
| Split | train |
| Tokens per Condition | 1.5B |
| Total Training | 9B tokens (6 conditions) |

### 4.2 Evaluation Dataset

| Attribute | Value |
|-----------|-------|
| Name | LongBench |
| Source | THUDM/LongBench (HuggingFace) |
| Version | v1 (original) |
| Tasks | 7 QA tasks (see FR-2) |
| Total Samples | ~1400 (full test splits) |

### 4.3 LongBench Tasks

| Task | Type | Avg Length | Samples |
|------|------|------------|---------|
| narrativeqa | Single-doc QA | ~18K | ~200 |
| qasper | Single-doc QA | ~5K | ~200 |
| multifieldqa_en | Single-doc QA | ~5K | ~200 |
| hotpotqa | Multi-doc QA | ~9K | ~200 |
| 2wikimqa | Multi-doc QA | ~5K | ~200 |
| musique | Multi-doc QA | ~11K | ~200 |
| triviaqa | Single-doc QA | ~8K | ~200 |

### 4.4 Length Bucket Strategy
- Truncate from middle to preserve instruction + question
- Pad shorter samples to target length
- Map natural lengths to nearest bucket

---

## 5. Model Specification

### 5.1 Teacher Model

| Attribute | Value |
|-----------|-------|
| Name | Phi-1.5 |
| Source | microsoft/phi-1_5 |
| Parameters | 1.3B |
| Hidden Dim | 2048 |
| Context Limit | 2048 (training), extrapolate to 32K |

### 5.2 Student Models (6 variants)

| ID | Objective | Training Length | Eval Lengths |
|----|-----------|-----------------|--------------|
| MOHAWK-4K | Matrix-level | 4K | 4K, 16K, 32K |
| MOHAWK-16K | Matrix-level | 16K | 4K, 16K, 32K |
| MOHAWK-32K | Matrix-level | 32K | 4K, 16K, 32K |
| CAB-4K | Token-level | 4K | 4K, 16K, 32K |
| CAB-16K | Token-level | 16K | 4K, 16K, 32K |
| CAB-32K | Token-level | 32K | 4K, 16K, 32K |

### 5.3 MOHAWK Distillation Loss
```python
L_matrix = MSE(student_mixer_matrix, teacher_attention_matrix)
# student_mixer_matrix = Mamba-2 M matrix
# teacher_attention_matrix = softmax(Q @ K.T / sqrt(d))
```

### 5.4 CAB Distillation Loss
```python
class AttentionBridge(nn.Module):
    def __init__(self, d_model, hidden_dim=None):
        hidden_dim = hidden_dim or d_model * 2
        self.q_to_b = nn.Sequential(nn.Linear(d_model, hidden_dim), nn.GELU(), nn.Linear(hidden_dim, d_model))
        self.k_to_c = nn.Sequential(nn.Linear(d_model, hidden_dim), nn.GELU(), nn.Linear(hidden_dim, d_model))

# Loss: MSE(B_student, bridge(Q)) + MSE(C_student, bridge(K))
```

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics

| Metric | Formula | Success Threshold |
|--------|---------|-------------------|
| F1 Score | Token-level F1 (LongBench) | Report per condition |
| F1 Retention | (student_F1 / teacher_F1) × 100 | Report % |
| Interaction Term | ANOVA A×B p-value | p < 0.05 |

### 6.2 Effect Size Predictions

| Length | Expected Effect | Threshold |
|--------|-----------------|-----------|
| P1 (4K) | MOHAWK ≈ CAB | Within 2 F1 points |
| P2 (16K) | CAB > MOHAWK | ≥3 F1 points |
| P3 (32K) | CAB > MOHAWK | ≥5 F1 points |

### 6.3 Gate Condition
**PASS:** 
1. Interaction term significant (p < 0.05)
2. P2 effect size ≥ 3 F1 points
3. P3 effect size ≥ 5 F1 points

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=2.0 | Core framework |
| transformers | >=4.35 | Model loading |
| mamba-ssm | >=1.0 | Mamba architecture |
| datasets | >=2.14 | LongBench/C4 loading |
| scipy | >=1.10 | ANOVA, t-tests |
| statsmodels | >=0.14 | 2-way ANOVA |
| matplotlib | >=3.7 | Visualization |
| seaborn | >=0.12 | Statistical plots |

### 7.2 Hardware Requirements
- GPU: 8× A100 80GB (training), 1× A100 (evaluation)
- RAM: 128GB (training), 64GB (evaluation)
- Storage: 100GB for checkpoints
- Training Time: ~4 weeks (6 conditions × 1.5B tokens)

### 7.3 External References
- MOHAWK: https://arxiv.org/abs/2408.10189, https://github.com/goombalab/phi-mamba
- CAB: https://arxiv.org/abs/2510.19266, https://github.com/wph6/CAB
- LongBench: https://arxiv.org/abs/2308.14508, https://github.com/THUDM/LongBench

---

## 8. Non-Functional Requirements

### NFR-1: Statistical Power
- Full LongBench test splits (~1400 samples total)
- Sufficient power for effect size detection
- No trivially small samples

### NFR-2: Reproducibility
- Fixed random seeds across conditions
- Log all hyperparameters
- Checkpoint at 500M token intervals

### NFR-3: Computational Efficiency
- bf16 mixed precision training
- Gradient accumulation for memory
- Streaming data loading

---

## 9. Success Criteria

### 9.1 PoC Pass Conditions
1. All 6 model variants trained successfully
2. Evaluation completes on full LongBench test splits
3. Interaction term (A×B) significant at p<0.05
4. P2: CAB advantage ≥3 F1 points at 16K
5. P3: CAB advantage ≥5 F1 points at 32K

### 9.2 Expected Outcome
- At 4K: Both objectives perform similarly (within training distribution)
- At 16K: CAB shows moderate advantage (emerging extrapolation benefit)
- At 32K: CAB shows strong advantage (representation stability pays off)

---

## 10. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Training compute insufficient | Medium | High | Use pre-trained MOHAWK, train only CAB variants |
| Interaction term not significant | Medium | High | Increase sample size, try 3-way interaction with task |
| CAB checkpoint unavailable | Low | Medium | Train from scratch with documented bridge |
| Memory overflow at 32K | Medium | Medium | Gradient checkpointing, reduced batch size |

---

## 11. Ablation Studies (Integrated)

### 11.1 Per-Task Analysis
Report F1 by task type to identify where CAB advantage is strongest.

### 11.2 Layer-wise Analysis
Analyze which teacher layers contribute most to CAB advantage (from H-M2 drift analysis).

### 11.3 Length Interpolation
Test at 8K intermediate length to verify smooth transition.

---

*Generated by Phase 3 Implementation Planning*
*Source: 02c_experiment_brief.md*
*Predecessor: H-M2 (validated CAB drift stability)*
