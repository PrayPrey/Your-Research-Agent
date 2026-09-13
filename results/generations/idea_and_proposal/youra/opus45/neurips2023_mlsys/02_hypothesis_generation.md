# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CLO-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under cloud datacenter deployment conditions with measurable carbon intensity variations, if a Carbon Lifecycle Optimizer (CLO) jointly optimizes training configuration and serving scheduling using predictive carbon amortization modeling with uncertainty quantification, then total ML model lifecycle carbon emissions will be reduced by 30-50% compared to independent training-only (CarbonGearRL) and serving-only (EcoServe) optimization, because training decisions (architecture, sparsity, quantization) causally determine serving-phase carbon intensity, and joint optimization exploits this coupling through a learned Carbon Amortization Model that predicts per-request serving carbon from training configuration features.

**Alternative Hypothesis (H0):**
Joint training-serving carbon optimization provides no statistically significant improvement over independent optimization of training and serving phases. The training-serving carbon relationship either does not exist, is not learnable, or the coupling benefit is negligible compared to phase-independent optimization.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Training Configuration | Independent | Architecture choice (model size 7B-70B, depth, width), sparsity level (0-90%), quantization (FP32/FP16/INT8), training duration (epochs) | Size: 7B-70B params; Sparsity: 0-90%; Quantization: FP32/FP16/INT8 |
| Geographic-Temporal Deployment | Independent | Cloud region selection from Electricity Maps API carbon intensity data; scheduling window (off-peak vs peak carbon hours) | Regions: US-West, EU-North, etc.; Carbon intensity: 50-800 gCO2/kWh |
| Total Lifecycle Carbon | Dependent | C_total = C_train + (N_requests × C_serve), measured in kg CO2-equivalent using CodeCarbon/Carbontracker | Expected: 100-10,000 kg CO2e per model lifecycle |
| Model Quality | Controlled | Accuracy/perplexity threshold maintained within ±2% of baseline; measured on standard benchmarks (MMLU, HellaSwag) | Quality degradation: ≤2% |
| Serving Workload Profile | Controlled | Fixed request distribution (QPS, sequence lengths) from production trace or synthetic workload | QPS: 10-1000; Sequence: 128-2048 tokens |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Training Configuration → Model Characteristics → Per-Request Serving Carbon → Total Lifecycle Carbon
        [Step 1]                [Step 2]                  [Step 3]
```

**Step 1: Training Configuration → Model Characteristics**
Training choices (architecture size, sparsity level, quantization) produce model artifacts with specific computational characteristics (FLOPs, memory footprint, activation patterns).

**Step 2: Model Characteristics → Per-Request Serving Carbon**
Model artifacts determine per-request energy consumption during inference. Smaller, sparser, quantized models require fewer FLOPs and memory accesses per inference.

**Step 3: Per-Request Carbon × Workload → Total Lifecycle Carbon**
Aggregated serving carbon plus training carbon equals lifecycle carbon: C_total = C_train + N_requests × C_serve.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Patterson et al. 2021 | Sparse models use <1/10th energy of dense models; 100-1000x variation by architecture choice | Strong |
| Step 2 → Step 3 | EcoServe 2025 | 4R framework achieves 47% carbon reduction; GPU dominates operational carbon | Strong |
| Step 3 → Outcome | LCA Methodology | Standard carbon amortization over product lifecycle; validated in environmental engineering | Strong |

**Key Tension:**
Patterson et al. (2021) focuses on training-phase optimization while EcoServe (2025) focuses on serving-phase optimization. Neither addresses the joint optimization opportunity where training decisions affect serving carbon.

**Resolution:** This hypothesis tests whether the Carbon Amortization Model can capture this coupling and whether joint optimization yields benefits beyond the sum of independent optimizations.

### 1.4 Key Assumptions

1. **Carbon Amortization Model Accuracy (A1)**
   - Assumption: CAM can achieve R² > 0.7 in predicting serving carbon from architecture features
   - Evidence: Patterson 2021 shows 100-1000x variation by architecture; OpenCarbonEval achieves accurate carbon prediction
   - Consequence if violated: Joint optimization reduces to independent optimization; hypothesis degrades to baseline

2. **Carbon Intensity Data Availability (A2)**
   - Assumption: Real-time carbon intensity data available via public APIs with hourly granularity
   - Evidence: Electricity Maps API provides hourly data globally
   - Consequence if violated: Temporal arbitrage component becomes ineffective; geographic-only optimization remains

3. **Training-Serving Relationship Learnability (A3)**
   - Assumption: Architecture features (params, FLOPs, memory) correlate with inference energy
   - Evidence: OpenCarbonEval methodology; EcoServe embodied/operational carbon analysis
   - Consequence if violated: CAM cannot generalize; hypothesis fails on mechanism sub-hypothesis

4. **Workload Predictability (A4)**
   - Assumption: Serving workload can be estimated within order of magnitude
   - Evidence: EcoServe shows 55% of inference workload is predictable batch jobs
   - Consequence if violated: Uncertainty bounds widen; robust optimization becomes conservative

### 1.5 Scope & Boundaries

**Applies To:**
- Cloud-deployed ML models with both training and serving phases
- LLMs (7B-70B parameters), vision models, general deep learning
- Organizations with carbon reduction mandates or sustainability goals
- Workloads with measurable serving request volumes (>10K requests/day)

**Does NOT Apply To:**
- Edge-only deployment without cloud training
- One-shot models with no serving phase
- Real-time latency-critical applications where carbon optimization is secondary
- Environments without carbon intensity data access

**Known Limitations:**
- Requires historical carbon tracking data for CAM training (cold-start problem)
- Conservative optimization under high workload uncertainty
- Does not address embodied carbon of hardware manufacturing

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Lifecycle Carbon Reduction vs Independent Baseline):**
If CLO jointly optimizes training configuration and serving scheduling, then total lifecycle carbon (C_total) will be 30-50% lower than CarbonGearRL (training) + EcoServe (serving) independent optimization baseline.

*Measurement:*
- Lifecycle carbon reduction ≥30% with p < 0.05
- Statistical test: Paired t-test across 5+ model architectures, n ≥ 20 runs per configuration

*Success Criteria for Phase 2B:*
- Primary: Lifecycle carbon reduction ≥30% (p < 0.05)
- Falsification: Lifecycle carbon reduction <15% triggers rejection

**Secondary Predictions:**

**P2 (Carbon Amortization Model Calibration):**
If uncertainty quantification is used in CAM, then actual carbon emissions will fall within predicted 90% confidence bounds for ≥90% of test cases.

**P3 (Scaling Benefit):**
If serving workload increases 2x, then CLO benefit over baseline will increase (not decrease), demonstrating that training-serving coupling becomes more valuable at scale.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Lifecycle carbon reduction <15% compared to independent baseline
2. **Mechanism Failure:** Carbon Amortization Model achieves R² < 0.5
3. **Comparative Failure:** No advantage on any dimension (carbon, quality, cost) over independent baseline

### 1.7 SOTA Baseline (SOTA Comparison Mode)

| Method | Focus | Carbon Reduction | Year | Limitation |
|--------|-------|------------------|------|------------|
| CarbonGearRL | Training | 52% | 2025 | Training-only; ignores serving phase |
| EcoServe | Serving | 47% | 2025 | Serving-only; ignores training decisions |
| GAIA | Batch serving | 57% | 2024 | Batch jobs only; no lifecycle view |

**CLO Target:** 30-50% additional lifecycle reduction beyond independent optimization

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large effect expected)
- Required runs: n ≥ 20 per configuration
- Statistical power: 0.8
- Model architectures: 5+ (7B, 13B, 30B, 70B variants)

**Test Specification:**
- Method: Paired t-test (same model architectures, same workload profiles)
- Significance level: α = 0.05 (one-tailed)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does joint training-serving carbon optimization achieve measurably lower lifecycle emissions than independent optimization under cloud datacenter conditions with varying carbon intensity?"

- Maps to: Primary prediction (P1)
- Verification type: Empirical (lifecycle carbon measurement)
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the Carbon Amortization Model the actual mechanism enabling lifecycle carbon reduction through training-serving coupling?"

- Maps to: Causal mechanism (N=3 steps)
- Decomposition in Phase 2B:
  - H-M1: Training Configuration → Model Characteristics
  - H-M2: Model Characteristics → Per-Request Serving Carbon
  - H-M3: Aggregation → Total Lifecycle Carbon
- Verification type: Causal analysis with ablations
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does CLO outperform CarbonGearRL + EcoServe independent baseline by ≥30% on lifecycle carbon while maintaining model quality?"

- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CLO-v1
- [x] Confidence level specified: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table complete)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 total with primary marked)
- [x] Falsification criteria are defined with quantitative thresholds
- [x] Baselines are identified for comparison (CarbonGearRL, EcoServe)
- [x] SH1, SH2, SH3 are clear starting points for Phase 2B

### Open Questions

1. **Data Availability:** What datasets exist for training the Carbon Amortization Model? Options include MLPerf training traces, Azure/GCP published carbon data, or synthetic generation from power models.

2. **Cold-Start Problem:** How to bootstrap CAM for new model architectures not seen during training? Consider transfer learning or architecture feature embedding approaches.

3. **Verification Priority:** Should we verify SH1 (existence) first, then SH2 (mechanism), finally SH3 (comparison)?

4. **Resource Requirements:** Estimated compute for full validation: 5 model scales × 20 runs × 2 phases = 200 experiment runs.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
