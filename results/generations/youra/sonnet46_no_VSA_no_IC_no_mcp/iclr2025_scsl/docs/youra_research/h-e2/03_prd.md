---
stepsCompleted: ["executive-summary", "problem-statement", "functional-requirements", "nfr", "data-specification", "evaluation-metrics", "dependencies", "success-criteria"]
hypothesis_id: h-e2
tier: LIGHT
generated_at: 2026-08-26T00:00:00Z
---

# Product Requirements Document: H-E2

**Hypothesis:** The paradigm effect on spurious/task probe accuracy ratio is observable on CelebA balanced test split, and may differ in magnitude from Waterbirds.
**Type:** EXISTENCE (PoC replication study)
**Tier:** LIGHT (≤15 tasks)
**Base Hypothesis:** H-E1 (VALIDATED)

---

## 1. Executive Summary

H-E2 replicates the H-E1 linear-probe paradigm comparison on CelebA instead of Waterbirds. The entire pipeline (4 ResNet-50 backbones, sklearn linear probes, ANOVA + Bonferroni statistics) is reused verbatim from H-E1; only the dataset loader changes. The primary scientific question is whether the paradigm effect (MoCo-v3 lowest spurious encoding) holds on CelebA's gender-based spurious correlation, and whether the magnitude differs from Waterbirds' texture-based correlation.

**Gate:** SHOULD_WORK — failure logs a limitation and does not block Phase 5.

---

## 2. Problem Statement

### 2.1 Motivation
H-E1 demonstrated a significant paradigm effect (ANOVA F=35.99, p=2.42e-7) on Waterbirds (95% spurious correlation, background texture). CelebA has a structurally different spurious correlation (demographic: ~94% of blond train samples are female) and different visual modality. Whether the paradigm effect generalizes across dataset types is a prerequisite for broader claims in H-D1.

### 2.2 Scientific Question
Does the paradigm (ERM/MoCo-v3/DINO/BarlowTwins) significantly affect the spurious/task probe accuracy ratio on CelebA? Does the rank ordering (MoCo-v3 lowest) replicate?

### 2.3 Approach
- Controlled experiment: identical pipeline to H-E1, only dataset changes
- CelebA: task=Blond_Hair (attr 9), spurious=Male (attr 20)
- Balanced test: 4 groups × 180 samples = 720 total
- 5 seeds, 40 probe runs (4 paradigms × 2 targets × 5 seeds)

---

## 3. Functional Requirements

### FR-1: CelebA Dataset Loading
- **Action:** Load CelebA via `torchvision.datasets.CelebA` (auto-download, `download=True`)
- **Cache path:** `./data/celeba/` (torchvision default)
- **Target attributes:** Blond_Hair (index 9), Male (index 20)
- **Preprocessing:** Resize(256) → CenterCrop(224) → ToTensor → Normalize(ImageNet)
- **Acceptance:** Dataset loads without error; `len(celeba_test)` == 19962

### FR-2: Group-Balanced Test Sampler
- **Action:** Sample equal n from 4 groups in test split: (Blond+Male), (Blond+Female), (Non-blond+Male), (Non-blond+Female)
- **n_per_group:** 180 (minimum group size in CelebA test)
- **Total:** 720 balanced test samples
- **Acceptance:** All 4 groups exactly 180 samples; indices cover all 4 combinations

### FR-3: Feature Extraction (4 Paradigms)
- **Action:** Load 4 cached ResNet-50 checkpoints (H-E1 cache `~/.cache/torch/hub/checkpoints/`), extract 2048-dim avgpool features on balanced CelebA test
- **Paradigms:** ERM (torchvision), MoCo-v3 (facebookresearch/moco-v3), DINO (facebookresearch/dino:main), BarlowTwins (facebookresearch/barlowtwins:main)
- **No redownload:** Checkpoints already cached from H-E1
- **Acceptance:** Feature tensor shape (720, 2048) per paradigm; extracted with `torch.no_grad()`

### FR-4: Linear Probe Training (Task + Spurious per Paradigm per Seed)
- **Action:** Train sklearn LogisticRegression probes on CelebA train features (full train split)
- **Probe targets:** Blond_Hair (task), Male (spurious)
- **Hyperparams:** C=1.0, max_iter=1000, solver=lbfgs, random_state=seed
- **Seeds:** 5 (0–4, matching H-E1 exactly)
- **Total runs:** 40 (4 paradigms × 2 targets × 5 seeds)
- **Acceptance:** All 40 probes achieve accuracy > 0.5 (above balanced chance)

### FR-5: Ratio Computation and Statistical Analysis
- **Action:** Compute ratio = spurious_acc / task_acc per paradigm per seed; run one-way ANOVA across 4 paradigms; run 6 pairwise t-tests with Bonferroni correction (α=0.0083)
- **Statistics:** F-statistic, p-value (ANOVA); p_bonf, mean_diff, Cohen's d (pairwise)
- **Assertion:** `assert ratio > 0.5, "Degenerate probe"` after each probe run
- **Acceptance:** ANOVA runs without error; all 6 pairs reported

### FR-6: Waterbirds Cross-Dataset Comparison
- **Action:** Load H-E1 ratio results from `docs/youra_research/h-e1/` and compute per-paradigm difference (CelebA ratio − Waterbirds ratio)
- **Acceptance:** Comparison table produced with 4 paradigm rows × 2 dataset columns

### FR-7: Visualization
- **Mandatory:** Bar chart — CelebA ratio per paradigm (4 bars, error bars=std over seeds), horizontal dashed lines at H-E1 Waterbirds ratio values
- **Additional (autonomous):**
  1. Waterbirds vs CelebA grouped bar chart (2×4)
  2. Task/spurious accuracy breakdown per paradigm (paired bars)
  3. Seed-level strip plot (ratio per paradigm, 5 points each)
  4. P-value heatmap (4×4 Bonferroni-corrected matrix, upper triangle)
- **Save path:** `docs/youra_research/h-e2/figures/`
- **Acceptance:** All figures saved as PNG; mandatory figure exists

### FR-8: Results Logging and Report
- **Action:** Log per-run: `"CelebA: paradigm={p}, seed={s}, task_acc={:.4f}, spur_acc={:.4f}, ratio={:.4f}"`
- **Output:** Results JSON/CSV + summary report in `docs/youra_research/h-e2/`
- **Gate evaluation:** At least 1 pair with p_bonf < 0.05 AND diff ≥ 0.02 → GATE PASS

---

## 4. Data Specification

### 4.1 Primary Dataset: CelebA

| Field | Value |
|-------|-------|
| Name | CelebA (Large-scale CelebFaces Attributes) |
| Source | torchvision.datasets.CelebA (auto-download) |
| Download | `CelebA(root='./data', split='test', target_type='attr', download=True)` |
| Cache path | `./data/celeba/` |
| Total images | 202,599 |
| Train | 162,770 |
| Val | 19,867 |
| Test | 19,962 |
| Attributes | 40 binary; use indices 9 (Blond_Hair) and 20 (Male) |
| Image size | 178×218 → resize 256 → crop 224 |

**Note:** CelebA downloads from Google Drive via torchvision mirror. May require manual download fallback if Google Drive rate-limits. See FR-1.

**Group statistics (test split, approximate):**
| Group | Count |
|-------|-------|
| Blond + Male | ~180 |
| Blond + Female | ~1,387 |
| Non-blond + Male | ~7,535 |
| Non-blond + Female | ~10,860 |

### 4.2 Reused Infrastructure (H-E1)

| Component | Status | Path |
|-----------|--------|------|
| ERM checkpoint | Cached | `~/.cache/torch/hub/checkpoints/` |
| MoCo-v3 checkpoint | Cached | `~/.cache/torch/hub/checkpoints/` |
| DINO checkpoint | Cached | `~/.cache/torch/hub/checkpoints/` |
| BarlowTwins checkpoint | Cached | `~/.cache/torch/hub/checkpoints/` |
| Linear probe pipeline | Reuse verbatim | `docs/youra_research/h-e1/code/` |
| ANOVA + Bonferroni stats | Reuse verbatim | `docs/youra_research/h-e1/code/` |

---

## 5. Evaluation Metrics

### 5.1 Primary Metric
- **ratio** = spurious_probe_acc / task_probe_acc (per paradigm per seed)
- Range expected: [0.98, 1.15]
- Higher ratio → paradigm encodes spurious feature more strongly than task

### 5.2 Statistical Tests
| Test | Parameters |
|------|-----------|
| One-way ANOVA | 4 groups (paradigms), 5 obs each = 20 total |
| Pairwise t-test | 6 pairs (C(4,2)), Bonferroni α=0.05/6=0.0083 |
| Effect size | Cohen's d for each significant pair |

### 5.3 Gate Condition (SHOULD_WORK)
- **PASS:** ≥1 pair with p_bonf < 0.05 AND |ratio_diff| ≥ 0.02
- **FAIL:** No pair meets threshold → log limitation, continue to Phase 5

### 5.4 Cross-Dataset Comparison (H-D1 prerequisite)
- Per-paradigm: CelebA_ratio − Waterbirds_ratio
- Rank correlation: Spearman ρ between H-E1 and H-E2 paradigm rank orderings

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Seeds 0–4 used for all probe runs (matching H-E1 exactly for H-D1 paired comparison)
- Results saved to CSV/JSON for archival

### NFR-2: Performance
- Feature extraction: single forward pass per paradigm per split (no repeated extraction)
- Total runtime target: < 30 minutes on GPU (CelebA is larger than Waterbirds)

### NFR-3: Code Reuse
- Minimum 90% code reuse from H-E1 (only dataset loader and attribute indices differ)
- Do NOT refactor H-E1 code — copy and parameterize

### NFR-4: Assertions
- `assert ratio > 0.5, "Degenerate probe"` after each of 40 probe runs
- `assert features.shape == (N, 2048), f"Wrong feature shape: {features.shape}"`
- `assert len(balanced_idx) == 720, f"Balanced test size wrong: {len(balanced_idx)}"`

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.10
torchvision>=0.11
scikit-learn>=0.24
scipy>=1.7
numpy>=1.21
matplotlib>=3.4
seaborn>=0.11
pandas>=1.3
```

### 7.2 External Repositories (Reference Only)
- `facebookresearch/moco-v3` — MoCo-v3 hub (already cached from H-E1)
- `facebookresearch/dino` — DINO hub (already cached from H-E1)
- `facebookresearch/barlowtwins` — BarlowTwins hub (already cached from H-E1)

### 7.3 Local Dependencies
- H-E1 code (`docs/youra_research/h-e1/code/`) — source of reused pipeline
- H-E1 results — needed for FR-6 cross-dataset comparison

---

## 8. Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Code runs on CelebA without error | Required | P0 |
| All 40 probe runs complete (acc > 0.5) | Required | P0 |
| ANOVA + Bonferroni results produced | Required | P0 |
| Gate: ≥1 pair p_bonf<0.05, diff≥0.02 | SHOULD_WORK | P1 |
| Waterbirds comparison table generated | Required | P1 |
| Mandatory figure (bar chart) saved | Required | P1 |
| Results logged per FR-8 format | Required | P2 |
| All additional figures generated | Optional | P3 |
