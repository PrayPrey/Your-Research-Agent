# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-15T02:56:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: No Large-Scale API-Based Cross-Repository Documentation Completeness Measurement
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: Pre-registered, falsifiable hypothesis with explicit effect size (β ≥ 0.15) and disconfirmation (β < 0.05) criteria. Technically feasible population-scale design grounded in prior DTS validation, policy recommendations, and reuse modeling.

### Key Insights

1. **Scale matters**: 100x increase from Rondina et al. 2025 reveals population-level patterns invisible in small samples — this is not an incremental contribution.
2. **Weighted DTS is essential**: Simple Presence Average masks the critical asymmetry between easy-to-fill fields (Uses=0.95) and substantive fields (Collection Processes=0.10). Inverse-frequency weighting turns this from a finding into a design principle.
3. **Infrastructure design is empirically testable**: The 2021 HF YAML adoption is a quasi-natural experiment nobody has exploited.
4. **Minimum viable hypothesis is publication-sufficient**: Cross-repository audit + usage regression is novel and immediately achievable; causal panel machinery becomes robustness analysis.

### Breakthrough Moments

1. **Exchange 7** (Dr. Ally): Within-HF quasi-natural experiment (pre/post-2021) design resolved selection bias concern by holding contributor population more constant.
2. **Exchange 11** (Dr. Sage): "Minimum viable claim" clarification focused the hypothesis on immediately testable contributions — cross-repo disparity + usage prediction.
3. **Exchange 13** (Dr. Ally): Weighted DTS scoring (inverse-frequency from Rondina et al. Table 2) turned Prof. Rex's criticism into a concrete design improvement.

---

## Final Hypothesis

### Title
Infrastructure-Mediated Documentation Completeness and Dataset Reuse in ML Repositories

### Hypothesis ID
H-DocComp-v1

### Core Claim
Under ML dataset ecosystems across three major public repositories (HuggingFace Hub, OpenML, UCI ML Repository), if repository metadata infrastructure provides structured YAML templates with enforced fields (as HuggingFace post-2021 vs. legacy OpenML/UCI), then DTS-weighted documentation completeness will be significantly higher for structured repositories AND completeness score will significantly predict dataset download volume (standardized β ≥ 0.15), because structured templates lower documentation friction, improving search filter eligibility and discoverability, which drives downstream adoption.

### Mechanism

1. **Structured metadata infrastructure → Higher DTS-weighted completeness**: YAML templates lower friction for documenting standard fields. HF post-2021 shows highest completeness in Rondina et al. 2025.
2. **Higher completeness → Improved search discoverability**: HF search explicitly filters by task_categories and language — null fields exclude datasets from filtered queries. Jain et al. 2024 Croissant-RAI establishes structured metadata → discoverability link.
3. **Improved discoverability → Higher dataset reuse**: Koch et al. 2021 methodology for measuring reuse. Temporally ordered panel test: Completeness_t → Visibility_t+1 → Downloads_t+2.

---

## Predictions

### P1 (Primary): Cross-Repository Completeness Disparity
- **Statement**: HuggingFace Hub datasets have significantly higher DTS-weighted completeness than OpenML and UCI after controlling for age, task, organization type
- **Test**: ANOVA + multivariate regression with repository indicator
- **Success**: HF > OpenML AND HF > UCI, both p < 0.05 (Bonferroni), Cohen's d ≥ 0.3
- **Falsification**: No significant difference after controls

### P2 (Primary): Completeness Predicts Usage
- **Statement**: DTS-weighted completeness score significantly predicts download count (standardized β ≥ 0.15) in pre-registered negative binomial regression
- **Test**: NB regression: Downloads = β₀ + β₁·WeightedDTS + β₂·log(Age) + β₃·LaggedDownloads + γ_repo + δ_task
- **Success**: β₁ significant (p < 0.05), standardized β₁ ≥ 0.15
- **Falsification**: Standardized β₁ < 0.05 after all controls

### P3 (Secondary): Infrastructure Causal Test
- **Statement**: Within HF, post-2021 datasets show higher completeness than pre-2021 beyond age effects (DiD interaction)
- **Test**: Difference-in-differences: (Post2021 × HF) with OpenML/UCI as parallel control
- **Success**: Significant positive DiD interaction (p < 0.05); parallel pre-trends pass
- **Falsification**: No significant DiD interaction or pre-trends violated

---

## Novelty

### What's New
1. First population-scale (100K+ datasets) DTS-validated automated cross-repository completeness audit
2. First pre-registered causal test of structured metadata infrastructure effects on documentation quality
3. First empirical test of completeness → discoverability → reuse pathway in ML ecosystems
4. Inverse-frequency weighted DTS scoring that prioritizes rare high-effort documentation sections

### How It Differs from Prior Work
| Prior Work | Limitation | Our Contribution |
|-----------|------------|-----------------|
| Rondina et al. 2025 (DTS, 100 datasets) | Manual, small-N, no usage prediction | 100x scale, automated, usage regression |
| Oreamuno et al. 2024 (HF-only) | Single repository, no causal test | Cross-repo, DiD causal design |
| Koch et al. 2021 (reuse patterns) | No completeness variable | Completeness as predictor |
| Bhardwaj et al. 2024 (NeurIPS rubric) | Conference-specific, small-N | Population-scale, multi-repo |

---

## Experimental Design

### Data Sources
- **HuggingFace Hub**: `list_datasets(full=True)` → ~100K datasets, card_data YAML fields
- **OpenML**: REST API `list_datasets()` → ~4K datasets, metadata dataframe
- **UCI**: `ucimlrepo` package → ~600 datasets, structured metadata

### Scoring
- **DTS-Weighted Completeness**: Binary field presence per 6 DTS sections, inverse-frequency weighted using Rondina et al. 2025 Table 2 prevalences
- **Validation**: 120-dataset blinded human rating holdout (r ≥ 0.70, κ ≥ 0.75 targets)

### Statistical Models
- ANOVA + Bonferroni (cross-repo comparison, P1)
- Negative binomial regression, pre-registered (usage prediction, P2)
- Difference-in-differences (infrastructure test, P3)
- Sequential mediation: WeightedDTS_t → Visibility_t+1 → Downloads_t+2

---

## Limitations

1. **UCI scale**: Only ~600 UCI datasets vs. ~100K HF — stratified sampling required for fair comparison
2. **Semantic vs. structural completeness**: Automated scoring captures field presence, not content quality — validation study is required, not optional
3. **Selection bias**: HF may attract more documentation-aware contributors independent of YAML structure — within-HF DiD partially addresses this
4. **YAML adoption mandatory vs. optional**: DiD causal interpretation requires verifying that 2021 YAML change was mandatory/standardized

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Converged at Exchange 15 (15 exchanges) |
| **Clarity Verified** | Yes |
| **Pre-registered Specification** | Yes — NB regression with effect size thresholds |
| **Remaining Objections** | Selection bias (mitigated); YAML mandatory? (verify empirically) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Gap: gap-1 | Hypothesis: H-DocComp-v1 | Exchanges: 15 | All personas participated*
