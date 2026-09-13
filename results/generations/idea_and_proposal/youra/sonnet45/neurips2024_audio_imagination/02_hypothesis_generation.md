# Phase 2A Extended: Hypothesis Summary (Phase 2B Ready)

**Date:** 2026-02-06
**Author:** Pray
**Hypothesis ID:** H1-ChunkFlow
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
Real-time multimodal audio generation (<75ms end-to-end latency) can be achieved through chunk-based flow matching with adaptive quality selection, maintaining perceptual quality (CLAP score >0.65) and reducing power consumption by 2x compared to GPU-only baselines.

**Primary Innovation:** First streaming architecture for multimodal video-to-audio generation combining flow matching decomposition (200ms chunks, 50ms overlap), video ABR-inspired adaptive quality selection, FPGA hardware acceleration, and phase-coherent chunk stitching.

**Target Gap:** Gap 2 - Real-Time and Low-Latency Multimodal Audio Generation (NeurIPS 2024 Audio Imagination Workshop)

**Feasibility Confidence:** 0.82/1.0 (High) - validated by 4-agent party mode discussion

---

## Core Technical Approach

### Architecture Components

1. **Chunk-Based Flow Matching**
   - 200ms audio chunks with 50ms overlap
   - Flow matching ODE decomposition with boundary conditions
   - Overlap-add + phase vocoder for seamless stitching

2. **Adaptive Quality Selection**
   - GRU resource predictor (from video ABR domain)
   - Three quality tiers: High (50 steps), Medium (30 steps), Low (20 steps)
   - Maintains CLAP >0.65 across all tiers

3. **FPGA Hardware Acceleration**
   - Xilinx VU13P with SVD model compression
   - 16-bit fixed-point arithmetic
   - Target: <15W power (vs. 30W GPU baseline)

4. **Phase-Coherent Stitching**
   - Overlap-add for temporal continuity
   - Phase vocoder for spectral discontinuity elimination
   - Target: <-40dB discontinuity (inaudible artifacts)

### Performance Targets

| Metric | Baseline (AudioGen-Omni) | ChunkFlow Target | Improvement |
|--------|-------------------------|------------------|-------------|
| **Latency** | 238ms/chunk | <75ms | **3.2x faster** |
| **CLAP Score** | ~0.70 | >0.65 | -7% acceptable |
| **Power** | ~30W (GPU) | <15W (FPGA) | **2x efficient** |
| **Real-time** | No (24% RTF) | Yes (<1.0 RTF) | **Enables streaming** |

---

## Key Predictions (Testable)

**P1 (Primary): Latency**
- ChunkFlow achieves <75ms P95 latency for first 200ms chunk
- Measurement: Time from video frame input to first audio output
- Success: P95 <75ms on VGGSound validation set (100 samples)

**P2: Quality Maintenance**
- CLAP score >0.65 across all quality tiers (High/Medium/Low)
- Degradation between High and Low tiers <0.10
- MOS >3.5 for all tiers (15-20 human raters)

**P3: Power Efficiency**
- FPGA backend <15W average power (High quality tier)
- >2x efficiency vs. V100 GPU baseline (~30W)
- Measured via direct power meter

**P4: Phase Coherence**
- Spectral discontinuity at chunk boundaries <-40dB
- Measured via automated spectrogram analysis
- Validates overlap-add + phase vocoder effectiveness

### Falsification Criteria

The hypothesis is **FALSIFIED** if:
1. **Critical:** P95 latency >100ms (even with Low quality tier)
2. **Critical:** CLAP score <0.60 OR MOS <3.0 (High tier)
3. **Major:** FPGA power >20W OR <1.5x efficiency vs. GPU
4. **Major:** Spectral discontinuity >-30dB consistently

---

## Key Assumptions & Risks

### Critical Assumptions

**A1: Flow Matching Decomposability (HIGH RISK)**
- Assumption: 200ms chunks with 50ms overlap maintain quality
- Risk: Temporal dependencies may span >250ms
- Mitigation: SH1 ablation study (100/200/400ms chunks)

**A2: ABR Transfer Validity (HIGH RISK)**
- Assumption: GRU resource prediction transfers from video bandwidth to audio compute
- Risk: Different dynamics between network and compute constraints
- Mitigation: SH2 comparative study (GRU vs. heuristic vs. oracle)

**A3: 16-bit Precision Sufficiency (MEDIUM RISK)**
- Assumption: FPGA 16-bit arithmetic maintains quality
- Risk: Flow matching numerical instability under quantization
- Mitigation: SH3 precision ablation (32/16/8-bit)

---

## Related Work & Differentiation

### Primary Baseline: AudioGen-Omni (Wang et al., 2025)
- SOTA offline multimodal audio generation
- Limitation: 1.91s for 8s audio (non-real-time)
- ChunkFlow: 3.2x faster, enables streaming

### Supporting Foundations
- **ImmersiveFlow (2026):** Flow matching for audio (offline)
- **SyncSpeech (2025):** Low-latency TTS (speech-only)
- **RAVE (2021):** Fast synthesis (timbre transfer only)
- **Pensieve (2017):** Video ABR with GRU prediction

### Novel Contributions
1. **First real-time streaming multimodal audio generation** (<100ms latency)
2. **Cross-domain transfer:** Video ABR techniques → audio generation
3. **First FPGA deployment** of flow matching audio models
4. **Phase-coherent chunk stitching** for flow matching outputs

---

## Phase 2B Decomposition (Sub-Hypotheses)

### SH1: Existence (Chunk-Based Generation Feasibility)
**Question:** Can chunk-based flow matching generate coherent audio with acceptable quality?

**Experiment:**
- Ablate chunk size (100/200/400ms) × overlap (25/50/100ms)
- Compare vs. full-sequence baseline (AudioGen-Omni style)
- Metrics: CLAP score, MOS, phase discontinuity

**Success:** CLAP degradation <0.05 vs. baseline, discontinuity <-40dB

---

### SH2: Mechanism (Adaptive Quality Effectiveness)
**Question:** Does adaptive quality selection maintain quality while reducing latency?

**Experiment:**
- Simulate resource constraints (30%/60%/90% load)
- Compare Fixed-High vs. Adaptive (GRU) vs. Heuristic
- Metrics: Average latency, CLAP score, quality tier distribution

**Success:** >20% latency reduction at 90% load, CLAP maintained >0.65

---

### SH3: Comparison (FPGA Acceleration Benefit)
**Question:** Does FPGA achieve 2x power efficiency vs. GPU with equivalent quality?

**Experiment:**
- Compare GPU (V100), FPGA (VU13P), Hybrid
- Ablate precision (32/16/8-bit) on FPGA
- Metrics: Power consumption, latency, CLAP/MOS

**Success:** FPGA <15W, latency <75ms, CLAP difference <0.03 vs. GPU

---

## Implementation Requirements

### Resources
- **Hardware:** 2× V100 GPU (training), 1× Xilinx VU13P FPGA (deployment)
- **Data:** VGGSound (200k training, 1k validation, 500 test)
- **Compute:** ~500 GPU hours (model training), ~100 FPGA hours (optimization)

### Timeline
- Phase 2B (Verification Planning): 2 weeks
- Phase 2C (Experiment Design): 3 weeks
- Phase 3 (Implementation Planning): 4 weeks
- Phase 4 (Implementation & Validation): 12-16 weeks
- **Total:** 6-12 months, 2-3 researchers (MEDIUM difficulty)

### Dependencies
- Flow matching codebase (ImmersiveFlow baseline)
- FPGA toolchain (Xilinx Vitis AI)
- Evaluation metrics (CLAP, PEAVS, MOS platform)

---

## Applications & Impact

### Immediate Applications
- **VR/AR:** Real-time audio synthesis for immersive experiences
- **Mobile Gaming:** Low-power audio generation on smartphones
- **Live Streaming:** On-the-fly video-to-audio for content creators

### Research Impact
- Establishes chunk-based streaming as viable for generative audio
- Demonstrates cross-domain transfer (video ABR → audio generation)
- Provides FPGA deployment template for future audio models

### Gap Coverage
- **Gap 2 (Primary):** Real-time multimodal audio generation
- **Gap 1 (Partial):** Introduces latency + phase coherence evaluation metrics
- **Gap 3 (Partial):** Adaptive quality provides coarse-grained controllability

---

## Open Questions for Phase 2B

1. **Optimal Configuration:** Is 200ms + 50ms universal, or category-specific?
2. **GRU Training:** Synthetic load traces vs. real-world profiling data?
3. **Phase Vocoder Alternatives:** Neural vocoders (HiFi-GAN) vs. classical?
4. **Spatial Audio Extension:** Can ChunkFlow enable streaming 7.1.4 generation?
5. **Latency Lower Bound:** What is theoretical minimum for chunk-based approach?

---

## Readiness Status

**Phase 2B Requirements:**
- ✅ Testable predictions with falsification criteria
- ✅ Sub-hypothesis decomposition (SH1/SH2/SH3)
- ✅ Statistical verification design (sample sizes, tests, controls)
- ✅ Resource requirements identified (hardware, data, compute)
- ✅ Risk mitigation strategies defined

**Next Step:** `/phase2b-planning` to develop detailed verification roadmap

---

**Full Documentation:** `02a_extended_hypothesis_full.md` (complete technical specification)

*Generated using YouRA Phase 2A Extended Workflow (YOLO Mode)*
*2026-02-06*
