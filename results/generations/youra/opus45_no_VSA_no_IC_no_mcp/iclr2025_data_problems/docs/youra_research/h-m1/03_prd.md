# Product Requirements Document: H-M1

**Hypothesis:** Perplexity filtering controls the quality-diversity tradeoff: intermediate thresholds (p30-p60) outperform both extremes (no filter, p90) because they retain diverse content while excluding noise.

**Date:** 2026-08-28
**Author:** PrayPrey
**Type:** MECHANISM (builds on H-E1)

---

## Executive Summary

This experiment tests the **mechanism** behind H-E1's dose-response finding. We hypothesize that intermediate perplexity filtering improves model training by balancing quality (noise exclusion) against diversity (content retention). The mechanism manifests as faster convergence for filtered data vs. unfiltered, with both extremes (no filter, very strict) underperforming moderate filtering.

---

## Problem Statement

H-E1 established that perplexity filtering exhibits a concave dose-response curve with peak performance around p50-p54. This PRD specifies experiments to test **why** this peak exists:

**Mechanism Hypothesis:** Noise dilution in unfiltered data slows convergence (gradient signal-to-noise ratio), while over-filtering reduces diversity and limits generalization.

---

## Functional Requirements

### FR-1: Data Pipeline

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Load RedPajama-v2 with streaming | P0 |
| FR-1.2 | Filter by `ccnet_perplexity` at 7 thresholds | P0 |
| FR-1.3 | Compute percentile thresholds from corpus sample | P0 |
| FR-1.4 | Tokenize with GPT-2 tokenizer | P0 |

**Configurations:**
- M1-C0: No filter (raw)
- M1-C1: p20 threshold
- M1-C2: p40 threshold
- M1-C3: p50 threshold (near H-E1 optimum)
- M1-C4: p60 threshold
- M1-C5: p80 threshold
- M1-C6: p90 threshold (very strict)

### FR-2: Model Training

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | GPT-2 125M architecture (12L, 768H, 12A) | P0 |
| FR-2.2 | AdamW optimizer (β1=0.9, β2=0.95, wd=0.1) | P0 |
| FR-2.3 | Cosine LR schedule, peak 6e-4, 2000 warmup | P0 |
| FR-2.4 | 10B tokens per configuration | P0 |
| FR-2.5 | Log loss every 100 steps | P0 |

### FR-3: Convergence Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Compute steps-to-threshold (loss < 3.5) | P0 |
| FR-3.2 | Compute convergence AUC (area under loss curve) | P0 |
| FR-3.3 | Compare loss at fixed token checkpoints (1B, 5B, 10B) | P0 |
| FR-3.4 | Statistical comparison via bootstrap | P1 |

### FR-4: Benchmark Evaluation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Evaluate on HellaSwag, ARC-Easy, PIQA, WinoGrande | P0 |
| FR-4.2 | Compute PC1 ensemble score | P0 |
| FR-4.3 | Compare benchmark vs convergence rate | P1 |

### FR-5: Visualization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Loss curves overlay (7 configs) | P0 |
| FR-5.2 | Steps-to-threshold bar chart | P0 |
| FR-5.3 | Quality-diversity tradeoff scatter | P1 |

---

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Training reproducibility | seed=42 |
| NFR-2 | Memory efficiency | <40GB GPU RAM |
| NFR-3 | Checkpoint frequency | Every 1B tokens |
| NFR-4 | Logging granularity | 100 steps |

---

## Success Criteria

### Primary (MUST_WORK Gate)

1. **Convergence Advantage**: p40-p60 configs reach loss=3.5 faster than p0 (unfiltered)
2. **Extreme Penalty**: Both p0 and p90 underperform p50 on benchmark ensemble
3. **Monotonic Pattern**: Convergence improves from p0→p50, then degrades p50→p90

### Secondary

4. **Effect Size**: Cohen's d > 0.5 for convergence rate difference (p50 vs p0)
5. **Benchmark Correlation**: Faster convergence correlates with higher benchmark scores

---

## Dependencies

- **H-E1 Results**: Validated dose-response curve (perplexity peak ~p54)
- **Infrastructure**: H-E1 training/evaluation pipeline (reuse)
- **Data**: RedPajama-v2 with `ccnet_perplexity` field

---

## Out of Scope

- Deduplication parameter sweep (covered in H-E1)
- Scale beyond 125M parameters
- Multi-seed runs (single seed for PoC)
