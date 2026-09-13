# H-E1 Hypothesis Context (JIT Generated from 02b_verification_plan.md)

**Generated:** 2026-03-15
**Source:** 02b_verification_plan.md (Phase 2B)
**Hypothesis:** H-E1 — DTS Measurement Feasibility

---

## Hypothesis Information

**ID:** H-E1
**Type:** EXISTENCE
**Statement:** Under the ML dataset ecosystem context (HF Hub, OpenML, UCI), if public APIs are queried for dataset metadata (card_data YAML, OpenML fields, ucimlrepo), then DTS-weighted documentation completeness scores are computable for ≥70% of the target corpus because structured API responses map reliably to the 6 DTS section categories.

**Rationale:** This hypothesis establishes that automated API-based DTS scoring is technically feasible at population scale — a prerequisite for all downstream mechanism and prediction tests. Without this foundation, the entire PROVE_NEW measurement approach fails (A1 violation). Validation against 120-dataset human annotation confirms automated score validity before proceeding.

**Gate:** MUST_WORK
**Prerequisites:** None (foundation hypothesis)

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset
- **Name:** Cross-Repository ML Dataset Metadata Corpus (API sampling)
- **Type:** custom (programmatic-api)
- **Source:** HuggingFace Hub API (list_datasets full=True), OpenML REST API, ucimlrepo Python package
- **Path:** Collected via API — no pre-existing file
- **Scale:** ~500 HF + 200 OpenML + 100 UCI = 800 minimum samples
- **Hypothesis Fit:** Public APIs provide structured metadata (card_data YAML, OpenML fields, UCI ucimlrepo) that directly operationalizes DTS field categories. No annotation required for primary scoring.

### Model
- **Name:** DTS 6-section binary scoring algorithm
- **Type:** statistical/algorithmic (no neural network)
- **Source:** scipy.stats, statsmodels, sklearn — custom implementation
- **Hypothesis Fit:** Binary presence scoring of 6 DTS sections (Motivation, Composition, Collection Process, Preprocessing, Uses, Distribution/Maintenance) maps directly to API field availability.

---

## Verification Protocol

1. Sample 500 HF + 200 OpenML + 100 UCI datasets (stratified by task_category and upload year 2016–2024).
2. Apply DTS 6-section binary scoring algorithm using predefined field→section mappings.
3. Compute per-section retrieval rate and overall weighted DTS score for all sampled datasets.
4. Validate automated scores against 120-dataset blinded human annotation (Pearson r ≥ 0.7 threshold).
5. Report coverage rate per repository per section; flag below-threshold sections for remediation strategy.

---

## Success Criteria

- **Primary:** Overall API-based DTS coverage rate ≥ 70% across combined corpus
- **Secondary:** Human-automated correlation r ≥ 0.70 on 120-dataset validation sample

---

## Failure Response

- IF coverage < 70%: PIVOT — supplement with README text parsing or relaxed DTS field mapping
- IF r < 0.70: EXPLORE — refine section-to-field mapping before proceeding to H-M1

---

## Baseline & Comparison Targets

| Baseline | Details |
|----------|---------|
| Rondina et al. 2025 | DTS schema on 100 popular datasets; section weights (inverse-frequency) |
| Oreamuno et al. 2024 | 71.52% of HF dataset cards undocumented; limited to 6,758 cards |
| Pushkarna et al. 2022 | Data Cards framework; HF YAML template adoption timeline |

---

## Dependencies

- **Depends on:** Nothing (root hypothesis)
- **Blocks:** H-M1, H-M2, H-M3

---

## Phase 2B Risk Assessment

- **R1 (Critical):** API field coverage insufficient — HF well-structured, OpenML/UCI less certain
- **R3 (High):** Age extraction failure — test age field extraction on pilot before full collection
- Mitigation: API pilot (50 datasets per repo) before full collection commitment
