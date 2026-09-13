# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HPD-v1
**Confidence Level:** 0.81

**Main Hypothesis:**
Under real-time audio generation conditions with latency requirements <100ms, if hierarchical predictive coding is applied to diffusion models via (1) coarse-to-fine hierarchical initialization and (2) precision-weighted adaptive NFE scheduling, then generation latency will decrease by 50-70% while maintaining audio quality within 10% of offline diffusion, because predictive initialization reduces diffusion steps needed and precision estimation enables adaptive computation allocation based on content complexity.

**Alternative Hypothesis (H0):**
Hierarchical predictive initialization provides no meaningful advantage over random noise initialization for diffusion-based audio generation; adaptive NFE scheduling based on precision estimation does not improve the latency-quality trade-off compared to fixed-step diffusion or consistency distillation alone.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Hierarchy depth (levels) | Independent | Number of prediction hierarchy levels: phoneme/event (10-50ms), segment (100-500ms), global context (1-5s) | 2-4 levels, default 3 |
| Precision threshold | Independent | Threshold for classifying segment as predictable vs unpredictable, calibrated per dataset via validation set | 0.3-0.7 (normalized precision score) |
| Max/Min NFE | Independent | Range of diffusion steps per segment | Min: 1-2 (predictable), Max: 4-8 (complex) |
| Generation latency (ms) | Dependent | Per-frame latency measured from input to audio output | Target: <50ms (vs baseline 100-200ms) |
| Audio quality (FAD) | Dependent | Fréchet Audio Distance compared to ground truth | Target: within 10% of full-step diffusion |
| MOS (Mean Opinion Score) | Dependent | Human perceptual quality rating | Target: ≥4.0 (1-5 scale) |
| Temporal consistency | Dependent | Boundary artifact score via automated detection | Target: <5% detectable artifacts |
| Model size | Controlled | Fixed parameter count matching baseline | ~500M parameters |
| Dataset | Controlled | Standard audio generation benchmarks | AudioCaps, VGGSound |
| Vocoder | Controlled | Mel-to-waveform conversion | BigVGAN (fixed) |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Hierarchical Prediction Network
    ↓ (provides structured initialization)
Step 2: Better Diffusion Starting Point
    ↓ (reduces steps to convergence)
Step 3: Precision-Weighted Adaptive NFE
    ↓ (allocates computation efficiently)
Step 4: Real-time Streaming Output
    → Outcome: <50ms latency with quality preservation
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | CogDPM (2024) | Hierarchical sampling with precision weighting improves diffusion convergence | Strong |
| Step2 → Step3 | Consistency Models | Better initialization reduces denoising steps needed | Strong |
| Step3 → Step4 | Marmoset auditory hierarchy (2021) | Brain allocates computation based on prediction error magnitude | Medium |
| Step4 → Outcome | SoundReactor (2025) | Frame-level streaming achieves 26.3ms with consistency training | Strong |

**Key Tension:**
- **Tension:** CogDPM demonstrates predictive coding improves diffusion forecasting, but operates on weather/wind data, not audio spectrograms. SoundReactor achieves low latency via consistency distillation alone without hierarchical prediction.
- **Resolution:** This verification plan tests whether combining hierarchical predictive initialization WITH adaptive NFE provides benefits beyond consistency distillation alone. Ablation experiments will isolate each component's contribution.

### 1.4 Key Assumptions

1. **A1: Coarse predictions provide useful initialization**
   - Evidence: CogDPM shows precision weighting improves convergence
   - Consequence if violated: No latency benefit from hierarchical structure; must fall back to pure consistency distillation

2. **A2: Segment complexity is predictable from content features**
   - Evidence: Brain literature shows predictable signals get precision weighting
   - Consequence if violated: Adaptive NFE becomes random allocation; no efficiency gain

3. **A3: Parallel segment processing maintains coherence**
   - Evidence: VoXtream's monotonic alignment, StreamMel's continuous mel approach
   - Consequence if violated: Audible boundary artifacts degrade quality

4. **A4: Consistency training synergizes with adaptive NFE**
   - Evidence: SoundReactor uses consistency for single-step segments
   - Consequence if violated: Two techniques may conflict rather than complement

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Text-to-audio streaming generation (TTA)
- Video-to-audio real-time synthesis (V2A)
- Text-to-speech with low latency requirements (TTS)
- Interactive audio for gaming, VR/AR applications
- Audio segments: 1-10 seconds per generation unit

**Where Hypothesis Does NOT Apply:**
- Long-form music generation (>30s) requiring global coherence
- Ultra-low latency (<30ms) real-time conversation systems
- High-fidelity music production requiring maximum quality
- Offline batch processing where latency is not a concern

**Known Limitations:**
- Precision estimation network adds ~5% computational overhead
- Requires training precision network alongside main diffusion model
- Optimal NFE range may vary significantly across audio domains

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Latency vs SOTA - Target <50ms):**
HPD will achieve per-frame generation latency <50ms on single H100 GPU while maintaining FAD within 10% of full-step (50-step) offline diffusion.

*Success Criteria for Phase 2B:*
- Primary: Latency <50ms AND FAD within 10% of offline baseline
- Stretch: Latency <35ms AND FAD within 5%
- Falsification: Latency >100ms OR FAD degradation >25%

**Secondary Predictions:**

**P2 (Adaptive NFE Efficiency):**
Precision-weighted adaptive NFE will reduce average compute (measured in NFE per segment) by 40-60% compared to fixed NFE, while maintaining equivalent quality.

**P3 (Hierarchical Initialization Benefit):**
Hierarchical predictive initialization will enable convergence in 50% fewer steps compared to random noise initialization, measured on held-out test segments.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** Latency >100ms on target hardware (H100)
2. **Quality Failure:** FAD degradation >25% compared to offline baseline
3. **Mechanism Failure:** Precision estimation shows <0.3 correlation with actual segment complexity
4. **Baseline Failure:** No improvement over consistency distillation alone (SoundReactor)

### 1.7 SOTA Baseline

| Method | Latency | Quality (FAD) | Approach | Year |
|--------|---------|---------------|----------|------|
| SoundReactor | 26.3ms | ~3.5 | Consistency distillation, frame-level V2A | 2025 |
| VoXtream | 102ms initial | ~3.0 | Monotonic alignment, full-stream TTS | 2025 |
| StreamMel | ~80ms | ~3.2 | Continuous mel-spectrogram, AR | 2025 |
| AudioLDM (offline) | 2-5s | ~2.0 | Latent diffusion, 50 steps | 2023 |

**HPD Target:** Latency 30-50ms, FAD 2.5-3.0

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 30 per configuration
**Test:** Paired t-test, α = 0.05 (one-tailed)
**Effect Size:** Cohen's d ~0.8 (large)
**Report:** Mean ± Std Dev, 95% CI, p-values with Bonferroni correction

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does hierarchical predictive initialization enable diffusion convergence in fewer steps than random initialization for audio generation?"
- Maps to: Primary prediction P3 (initialization benefit)
- Verification type: Empirical ablation
- Critical: MUST PASS to justify hierarchical architecture

**SH2 (Mechanism):**
"Does precision-weighted adaptive NFE allocation correctly identify segment complexity and allocate computation efficiently?"
- Maps to: Causal mechanism steps 3-4, prediction P2
- Verification type: Correlation analysis + ablation
- **Note:** Phase 2B will decompose into 4 sub-hypotheses (H-M1 through H-M4) based on N=4 causal chain length

**SH3 (Comparison):**
"Does HPD achieve better latency-quality trade-off than existing streaming methods (SoundReactor, VoXtream, StreamMel)?"
- Maps to: Primary prediction P1
- Verification type: Comparative empirical benchmark
- Critical: Determines practical value and publication worthiness

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-HPD-v1
- [x] Confidence level specified: 0.81
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence (9 variables defined)
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table complete)
- [x] Causal chain length determined: N=4
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions exist with primary marked (3 predictions)
- [x] Falsification criteria are defined (4 failure conditions)
- [x] Baselines identified for comparison (5 baselines)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What is the minimum GPU memory required for HPD training?
2. **Data Availability:** Is AudioCaps sufficient or do we need VGGSound for diverse sound events?
3. **Technical Feasibility:** How to handle variable-length segments in parallel processing?
4. **Verification Priority:** Should SH1 (existence) be tested first to validate architecture?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-13*
