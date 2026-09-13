# Configuration Document: h-m3 Validation

**Hypothesis ID:** h-m3  
**Date:** 2026-08-19  
**Type:** MECHANISM validation  
**Format:** Hardcoded dict (Python)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (extends h-m2)  
**Status:** Config pattern verified from h-m2/code/config.py  
**Config Files Found:** h-m2/code/config.py  
**Pattern Used:** Hardcoded dict (CONFIG = {...})

---

## Configuration Schema

Applied: Standard statistical testing patterns, h-m2 config structure.

```python
"""Configuration for h-m3: Required fields show no friction effect"""

CONFIG = {
    # Input Data (h-m2 cached extraction - no new API calls)
    "data": {
        "hf_metadata_path": "h-m2/data/raw/huggingface_metadata.json",
        "openml_metadata_path": "h-m2/data/raw/openml_metadata.json",
        "uci_metadata_path": "h-m2/data/raw/uci_metadata.json",
        "expected_counts": {
            "hf": 6500,
            "openml": 2990,
            "uci": 500,
        },
    },

    # Required Field Parsing Rules (platform-specific)
    "parsing": {
        "license": {
            "hf": {
                "reject_keywords": ["unknown", "other", "n/a", "none", ""],
                "case_insensitive": True,
            },
            "openml": {
                "reject_keywords": ["unknown", "other", "n/a", "none", ""],
                "case_insensitive": True,
            },
            "uci": {
                "accept_keywords": [
                    "cc-by", "cc by", "creative commons",
                    "mit", "apache", "gpl", "bsd", "lgpl",
                ],
                "case_insensitive": True,
            },
        },
        "version": {
            "hf": {
                "pattern": r"\d+\.\d+(\.\d+)?",  # Semantic version (X.Y or X.Y.Z)
            },
            "openml": {
                "type": "integer",  # OpenML uses integer versions
                "min_value": 0,
            },
            "uci": {
                "patterns": [
                    r"v?\d+\.\d+(\.\d+)?",  # Semantic (v1.0 or 1.0.1)
                    r"\d{4}-\d{2}-\d{2}",   # Date-based (2020-01-15)
                ],
            },
        },
    },

    # Statistical Thresholds (hypothesis-specific)
    "stats": {
        "p_threshold": 0.10,             # Chi-squared: p > 0.10 = no friction effect
        "cv_threshold": 0.20,            # Coefficient of variation < 0.20 = stable
        "cv_ratio_threshold": 0.25,      # Required CV / Optional CV < 0.25
        "cramers_v_threshold": 0.20,    # Cramér's V < 0.20 = weak association
        "mean_presence_threshold": 0.80, # Mean presence ≥ 80% = high absolute presence
        "laplace_smoothing": 1,          # Add +1 to contingency cells if zeros detected
    },

    # Validation Parameters
    "validation": {
        "sample_size": 100,
        "stratification": {
            "hf": 50,
            "openml": 30,
            "uci": 20,
        },
        "seed": 42,
        "agreement_threshold": 0.85,  # Target ≥85% manual agreement
    },

    # Output Options
    "output": {
        "generate_charts": True,
        "chart_format": "png",  # "png" or "svg"
        "chart_dpi": 300,
        "results_dir": "h-m3/data/results",
        "figures_dir": "docs/youra_research/h-m3/figures",
        "files": {
            "presence_rates": "h-m3/data/results/required_field_presence.csv",
            "validation_summary": "h-m3/data/results/validation_summary.json",
            "validation_sample": "h-m3/data/results/validation_sample.json",
            "comparison_table": "h-m3/data/results/comparison_table.md",
            "license_chart": "h-m3/data/results/license_presence_chart.png",
            "version_chart": "h-m3/data/results/version_presence_chart.png",
            "validation_report": "h-m3/04_validation.md",
        },
    },

    # h-m2 Contrast (for CV ratio calculation)
    "h_m2_reference": {
        "optional_field_cv": None,  # Loaded from h-m2 results at runtime
        "h_m2_results_path": "h-m2/data/results/statistical_results.json",
    },

    # Reproducibility
    "experiment": {
        "seed": 42,
        "deterministic": True,
        "verbose": True,
    },
}
```

---

## Threshold Rationale

### Statistical Thresholds

**p_threshold = 0.10** (Chi-squared test)
- Standard: p > 0.10 indicates no significant platform effect at 90% confidence
- Rationale: More permissive than typical α=0.05 to reduce false negatives; we want to confirm stability, not detect tiny differences
- h-m2 comparison: Optional fields showed p < 0.0001 (strong effect), so p > 0.10 demonstrates clear contrast

**cv_threshold = 0.20** (Coefficient of Variation)
- Formula: CV = std(presence_rates) / mean(presence_rates)
- Rationale: CV < 0.20 means standard deviation is <20% of mean, indicating tight clustering
- Example: If mean presence = 90%, std must be <18 percentage points
- h-m2 comparison: Optional CV likely >1.0 (high variance), so required CV <0.20 shows mechanism distinction

**cv_ratio_threshold = 0.25** (Required CV / Optional CV)
- Rationale: Required field variance should be <25% of optional field variance
- Example: If optional CV = 1.2, required CV must be <0.30 (but cv_threshold already requires <0.20)
- Purpose: Quantifies mechanism independence

**cramers_v_threshold = 0.20**
- Scale: 0 (no association) to 1 (perfect association)
- Interpretation: V < 0.20 = weak association between platform and presence
- Rationale: Standard cutoff for "negligible" effect size in contingency analysis

**mean_presence_threshold = 0.80**
- Rationale: 80% presence indicates strong enforcement (not just reduced friction)
- Distinguishes "high compliance" (enforcement) from "moderate improvement" (friction reduction alone)

**laplace_smoothing = 1**
- Applied only if zero cells detected in contingency table (e.g., UCI 0% for a field)
- Prevents chi-squared test failure due to division by zero in expected frequencies
- Standard Bayesian smoothing: add 1 to all cells before statistical test

---

## Parsing Rule Dictionaries

### License Parsing

**HuggingFace & OpenML:**
- Method: Reject keywords (non-empty string that isn't "unknown"/"other"/"none")
- Rationale: Both platforms have license dropdowns with explicit values
- Edge case: Empty strings or null → absent

**UCI:**
- Method: Accept keywords (must match known license types)
- Rationale: UCI has no structured license field; detect from prose/metadata
- Keywords: Creative Commons variants, OSI-approved licenses (MIT/Apache/GPL/BSD)
- Risk mitigation: Conservative matching (may undercount UCI), but parsing validation will catch misses

### Version Parsing

**HuggingFace:**
- Pattern: `\d+\.\d+(\.\d+)?` (semantic versioning)
- Example matches: "1.0", "2.3.1", "0.1.2"
- Rationale: HF encourages semantic versions in dataset cards

**OpenML:**
- Type: Integer (non-null, ≥0)
- Example: version=1, version=2
- Rationale: OpenML API returns integer version field

**UCI:**
- Patterns: Semantic (`v1.0`, `1.0.1`) or date-based (`2020-01-15`)
- Rationale: UCI has no structured version field; detect from metadata/file names
- Edge case: Multiple patterns increase recall for UCI's diverse formats

---

## Validation Strategy Parameters

### Stratified Sampling

**Sample Size: 100** (total manual review)
- **HuggingFace: 50** (50% of sample, matches 65% of dataset)
- **OpenML: 30** (30% of sample, matches 30% of dataset)
- **UCI: 20** (20% of sample, matches 5% of dataset, over-sampled for diversity)

**Rationale:**
- Over-sample UCI (20% vs 5%) to ensure adequate coverage of UCI's diverse formats
- 100 samples = reasonable manual review effort (2-3 hours)
- Stratification ensures platform-specific parsing rules are validated

### Agreement Threshold

**agreement_threshold = 0.85** (≥85% manual agreement)
- Numerator: Count of records where parser matches human judgment
- Denominator: 100 (total validation sample)
- Action if <85%: Refine parsing rules (especially UCI patterns) and re-validate

### Seed

**seed = 42** (fixed random seed)
- Ensures reproducible validation sample selection
- Matches h-m2 seed (consistency across hypotheses)

---

## Output Format Options

### Chart Generation

**generate_charts = True**
- Creates bar charts for license and version presence rates per platform
- X-axis: Platform (HF, OpenML, UCI)
- Y-axis: Presence rate (0-100%)
- Separate chart per field (2 total)

**chart_format = "png"**
- PNG: Default (smaller file size, good for reports)
- SVG: Optional (vector format, scalable for presentations)

**chart_dpi = 300**
- High-resolution for publication quality
- Standard for academic papers

### Output Files

**Core Results:**
- `validation_summary.json`: Statistical test results (chi-squared, Cramér's V, CV)
- `required_field_presence.csv`: Presence rates per platform (6 rows: 2 fields × 3 platforms)

**Validation:**
- `validation_sample.json`: 100-record sample with human review flags
- `comparison_table.md`: Required vs optional field comparison (markdown table)

**Visualizations:**
- `license_presence_chart.png`: Bar chart for license field
- `version_presence_chart.png`: Bar chart for version field

**Report:**
- `04_validation.md`: Full validation report (8 sections, per PRD FR-10)

---

## Configuration Usage Example

```python
from config import CONFIG

# Load data
hf_data = load_json(CONFIG["data"]["hf_metadata_path"])
assert len(hf_data) == CONFIG["data"]["expected_counts"]["hf"]

# Parse license field (HuggingFace)
def is_license_present_hf(record):
    license_val = record.get("license", "").lower()
    if not license_val:
        return False
    return license_val not in CONFIG["parsing"]["license"]["hf"]["reject_keywords"]

# Run chi-squared test
from scipy.stats import chi2_contingency
chi2, p, dof, expected = chi2_contingency(contingency_table)
is_stable = p > CONFIG["stats"]["p_threshold"]  # p > 0.10

# Apply Laplace smoothing if needed
if (contingency_table == 0).any():
    contingency_table += CONFIG["stats"]["laplace_smoothing"]

# Generate validation sample
import random
random.seed(CONFIG["validation"]["seed"])
sample = random.sample(hf_data, CONFIG["validation"]["stratification"]["hf"])
```

---

## Self-Validation

**Format Selection:**
- [x] Hardcoded dict only (no dataclass variant)

**Brevity:**
- [x] No ASCII diagrams
- [x] Archon KB search noted in 1 line ("Applied: ...")
- [x] Serena noted in Codebase Analysis section
- [x] Rationale only for non-standard values (p=0.10, CV<0.20)

**Serena MCP:**
- [x] Base hypothesis exists (h-m2) → Serena used to verify config pattern
- [x] Codebase Analysis section included

**Base Hypothesis Checks:**
- [x] h-m2/code/config.py read (actual implementation)
- [x] Config pattern verified (hardcoded dict)

**Content:**
- [x] Parsing rules: platform-specific dictionaries
- [x] Statistical thresholds: hypothesis-specific values with rationale
- [x] Validation parameters: stratification, seed, agreement threshold
- [x] Output options: chart format, file paths
- [x] Total length: ~300 lines (within 300-400 target)

---

**Configuration Complete** | **Next:** Code Implementation (Phase 4) | **Date:** 2026-08-19
