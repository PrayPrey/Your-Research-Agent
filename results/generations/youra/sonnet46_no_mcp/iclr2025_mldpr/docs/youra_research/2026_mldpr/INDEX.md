# Anonymous Pipeline Results - Complete Index

**Location:** `/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_mldpr_2/docs/youra_research/20260504_mldpr/`

**Summary:** 117 directories, 1,477 files | 3 Active Hypotheses | Full Pipeline Execution (Phases 0-6.5)

---

## Quick Navigation

### Root Level Documentation
- **00_brainstorm_session.md** - Phase 0 brainstorming results
- **01_targeted_research.md** - Phase 1 targeted literature research
- **01_targeted_research_full.md** - Phase 1 full research compilation
- **02b_verification_plan.md** - Phase 2B detailed verification plan
- **02_synthesis.yaml** - Phase 2A synthesis outputs
- **03_refinement.md** - Phase 2A refinement documentation
- **03_refinement.yaml** - Refinement data structure
- **045_validated_hypothesis.md** - Validated hypothesis summary
- **discussion_log.md** - Full discussion log across phases
- **verification_state.yaml** - Current verification state tracker

### Phase 2A - Round Table Discussion
- **01_round_table/00_metadata.yaml** - Round table metadata
- **01_round_table/final_opinions.yaml** - Final perspectives

---

## Hypothesis Implementations

### H-E1: Exploratory Hypothesis
**Path:** `h-e1/`

**Key Files:**
- `03_prd.md` - Product requirements
- `03_architecture.md` - Technical architecture
- `04_validation.md` - Validation results
- `code/run_experiment.py` - Main experiment script
- `results/existence_metrics.json` - FAIR metrics results
- `results/fair_scores.csv` - Fairness assessment scores
- `figures/gate_metrics_summary.png` - Gate metrics visualization

**Purpose:** Exploratory analysis of data existence and FAIR principles

---

### H-M1: Main Hypothesis 1
**Path:** `h-m1/`

**Key Files:**
- `03_prd.md` - Product requirements
- `03_architecture.md` - Technical architecture
- `04_validation.md` - Validation results
- `code/stratifier.py` - Data stratification logic
- `code/spearman_analyzer.py` - Statistical analysis
- `code/falsification.py` - Falsification detection
- `results/hm1_results.json` - Main results
- `experiment_results.json` - Raw experiment output
- `figures/fig_domain_stratification.png` - Stratification analysis

**Purpose:** Domain and era stratification analysis with falsification detection

---

### H-M2: Main Hypothesis 2
**Path:** `h-m2/`

**Key Files:**
- `03_prd.md` - Product requirements
- `03_architecture.md` - Technical architecture
- `04_validation.md` - Validation results
- `reflection_report.md` - Detailed reflection on results
- `code/run_experiment.py` - Main experiment script
- `code/src/matching.py` - Propensity score matching
- `code/src/survival_prep.py` - Survival analysis preparation
- `code/src/km_analysis.py` - Kaplan-Meier analysis
- `code/src/cox_analysis.py` - Cox regression analysis
- `code/src/sensitivity.py` - Sensitivity analysis
- `results/gate_result.json` - Gate analysis results
- `results/results.csv` - Comprehensive results table
- `figures/fig2_km_curves_matched.png` - Kaplan-Meier curves
- `figures/fig4_love_plot.png` - Love plot (covariate balance)
- `figures/fig5_cox_forest.png` - Cox hazard ratios

**Purpose:** Comprehensive survival analysis with propensity score matching and sensitivity analysis

---

## Paper Generation (Phases 5-6.5)

### Main Paper Files
**Path:** `paper/`

- **06_paper.md** - Initial paper draft
- **06_paper_r1.md** - Revision 1
- **06_paper_r2.md** - Revision 2
- **06_paper_final.md** - Final paper version
- **06_paper_checkpoint.yaml** - Paper generation state

### Paper Structure
**Path:** `paper/sections/`

- `00_abstract.md` - Abstract
- `01_introduction.md` - Introduction
- `02_related_work.md` - Related work review
- `03_methodology.md` - Methodology
- `04_experiments.md` - Experiments description
- `05_results.md` - Results presentation
- `06_discussion.md` - Discussion
- `07_conclusion.md` - Conclusion

### Figures Registry
- **figure_registry.yaml** - Figure metadata and references
- **06_narrative_blueprint.yaml** - Paper structure template
- **065_ground_truth.yaml** - Ground truth data for validation
- **06_references.bib** - Bibliography

### Paper Figures
**Path:** `paper/figures/`

- `gate_metrics_summary.png` - Gate metrics overview
- `fig2_km_curves_matched.png` - Matched KM curves
- `fair_distribution.png` - FAIR distribution
- `fig6_sensitivity_comparison.png` - Sensitivity analysis
- `fig4_love_plot.png` - Covariate balance plot
- `fig5_cox_forest.png` - Cox hazard ratios

### Adversarial Review (Phase 6.5)
**Path:** `paper/review/`

- **065_review_r1.md** - Round 1 adversarial review
- **065_review_r2.md** - Round 2 adversarial review
- **065_review_summary.md** - Review synthesis
- **065_changelog.md** - Changes implemented
- **065_review_checkpoint.yaml** - Review state
- **065_human_review_notes.md** - Human feedback notes

### LaTeX Compilation
**Path:** `paper/overleaf/`

- **main.tex** - Main LaTeX file
- **main.pdf** - Compiled PDF
- **references.bib** - Bibliography
- **sections/** - LaTeX section files
- **figures/** - Figure resources

---

## Research Materials

### Papers Collection
**Path:** `papers/`

Reference papers collected during Phase 1 research

### Paper Summaries
**Path:** `paper_summaries/`

Extracted summaries and key findings from reference papers

---

## Archive

### Previous Run
**Path:** `_archive/20260504T032828_routing_recovery/`

Complete snapshot of previous execution with routing error recovery:
- Previous hypothesis implementations (h-e1, h-m1)
- All documentation from earlier phases
- Cached research data (`.data_cache/`)
- Previous verification state

---

## File Organization Guide

### By Phase

| Phase | Location | Key File | Description |
|-------|----------|----------|-------------|
| 0 | Root | `00_brainstorm_session.md` | Brainstorming results |
| 1 | Root | `01_targeted_research.md` | Research compilation |
| 2A | Root + `01_round_table/` | `02_synthesis.yaml` | Dialogue & synthesis |
| 2B | Root | `02b_verification_plan.md` | Verification planning |
| 2C | `h-*/` | `02c_experiment_brief.md` | Experiment design |
| 3 | `h-*/` | `03_prd.md`, `03_architecture.md` | Architecture & planning |
| 4 | `h-*/code/` | `run_experiment.py`, `04_validation.md` | Code & validation |
| 5 | Root | `verification_state.yaml` | Baseline tracking |
| 6 | `paper/` | `06_paper_final.md` | Paper writing |
| 6.5 | `paper/review/` | `065_review_*.md` | Adversarial review |

### By Type

**Documentation:**
- `.md` files for narrative content
- `.yaml` files for structured data
- `.bib` files for references

**Code:**
- `code/src/` - Source modules
- `code/tests/` - Unit tests
- `code/config.py` - Configuration
- `code/run_experiment.py` - Main execution

**Results:**
- `results/` - JSON/CSV data outputs
- `figures/` - PNG visualizations
- `.omc/` - Execution state tracking

**Configuration:**
- `03_config.md` - Configuration documentation
- `03_tasks.yaml` - Task definitions
- `04_checkpoint.yaml` - Execution checkpoints

---

## Key Metrics & Outputs

### Statistics
- **Total Size:** ~1477 files across 117 directories
- **Active Hypotheses:** 3 (E1, M1, M2)
- **Paper Versions:** 3 revisions + final + 2 review rounds
- **Code Coverage:** ~40 test files covering 13+ source modules

### Main Results

**H-E1 (Exploratory):**
- FAIR metrics assessment
- Fairness distribution analysis
- Gate comparison metrics

**H-M1 (Main 1):**
- Domain stratification analysis
- Era-based stratification
- Falsification candidate detection

**H-M2 (Main 2):**
- Propensity score matching results
- Kaplan-Meier survival curves
- Cox regression analysis
- Sensitivity analysis (8 window sizes)

**Paper:**
- Complete ICML-format paper
- 8 section files + abstract
- 6 publication-ready figures
- 2 rounds of adversarial review
- LaTeX-compiled PDF ready for submission

---

## Access Patterns

### For Reading Results
1. Start with `verification_state.yaml` (overall status)
2. Review `045_validated_hypothesis.md` (summary)
3. Check specific hypothesis `04_validation.md` files
4. Examine `paper/06_paper_final.md` for final narrative

### For Understanding Methodology
1. Read `02b_verification_plan.md` (verification approach)
2. Review `h-*/03_architecture.md` (technical design)
3. Check `h-*/03_logic.md` (implementation details)
4. See `h-*/code/` for source code

### For Reproducing Results
1. Install: `code/requirements.txt`
2. Configure: `code/config.py`
3. Run: `code/run_experiment.py`
4. Validate: `code/tests/`
5. Check: `results/` and `figures/`

### For Writing/Presenting
1. Main narrative: `paper/06_paper_final.md`
2. Sections: `paper/sections/`
3. Figures: `paper/figures/`
4. Bibliography: `paper/06_references.bib`
5. LaTeX: `paper/overleaf/main.pdf`

---

## Helpful Files

- **DIRECTORY_TREE.txt** - Visual directory tree structure
- **COMPLETE_FILE_LIST.txt** - Detailed file listing with descriptions
- **INDEX.md** - This file

---

*Last Updated: 2026-05-20*
*Pipeline Status: Complete (Phases 0-6.5)*
