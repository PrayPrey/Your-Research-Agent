# H-E1 Human Annotation Guide

## Overview

This experiment requires **real human annotations** from 3 independent annotators to validate the base-rate of genuine safety violations in HH-RLHF rejected responses.

**IMPORTANT:** This experiment does NOT use synthetic/mock data. All annotations must come from actual human judgment.

---

## Quick Start

### Step 1: Generate Sample Set

First, generate the stratified sample of 500 responses:

```bash
python src/main.py --config config.yaml
```

This will create `data/samples.csv` but will fail at the annotation step (by design).

### Step 2: Collect Annotations from 3 Annotators

Each annotator should run the annotation CLI independently:

**Annotator 1:**
```bash
python -m annotation.cli --samples data/samples.csv --annotator 1
```

**Annotator 2:**
```bash
python -m annotation.cli --samples data/samples.csv --annotator 2
```

**Annotator 3:**
```bash
python -m annotation.cli --samples data/samples.csv --annotator 3
```

The CLI will:
- Present each sample with the prompt and rejected response
- Ask: "Is this a genuine safety violation? (y/n)"
- Save annotations to `data/annotations_annotator_<ID>.csv`
- Automatically merge into `data/annotations.csv` when all 3 complete

### Step 3: Run Full Experiment

Once all annotations are collected:

```bash
python src/main.py --config config.yaml
```

This will:
- Load the real annotations
- Calculate inter-annotator agreement (Cohen's κ)
- Compute base-rate via majority vote
- Perform binomial test for MUST_WORK gate
- Generate visualizations
- Output results to `outputs/results.json` and `outputs/report.md`

---

## Violation Criteria

Annotators should label a response as a **genuine violation** if it contains:

1. **Direct harm/violence encouragement**
2. **Toxic/offensive language**
3. **Privacy violations or personal information disclosure**
4. **Dangerous/illegal advice**
5. **Deception or misinformation**
6. **Other safety policy violations**

If the response is merely a marginal preference difference (e.g., slightly less helpful but not harmful), label it as **NOT a violation**.

---

## Expected Annotation Time

- **Training:** 1 hour (review criteria, calibration set)
- **Production:** 2-3 hours per annotator for 500 samples
- **Total:** ~3-4 hours per annotator

---

## Quality Control

The experiment will check:
- **Inter-annotator agreement:** Cohen's κ ≥ 0.60 (moderate agreement required)
- **Coverage:** All 500 samples must be annotated by all 3 annotators
- **Consistency:** Pairwise agreement heatmap generated for review

---

## File Structure

```
data/
├── samples.csv                    # Stratified sample (500 responses)
├── annotations_annotator_1.csv    # Annotator 1 judgments
├── annotations_annotator_2.csv    # Annotator 2 judgments
├── annotations_annotator_3.csv    # Annotator 3 judgments
└── annotations.csv                # Merged annotations (auto-generated)

outputs/
├── results.json                   # Experiment results
├── report.md                      # Summary report
└── figures/
    ├── base_rate.png              # Base-rate vs threshold
    ├── agreement_heatmap.png      # Inter-annotator agreement
    ├── violation_types.png        # Judgment distribution
    └── length_bias.png            # Violation rate by length quartile
```

---

## Troubleshooting

### "Annotation file not found" error

This is expected! The experiment requires real human annotations. Run the annotation CLI for all 3 annotators first.

### Resume interrupted annotation session

The annotation CLI saves progress incrementally. If interrupted, you can restart from the beginning (the CLI will warn about overwriting existing files).

### Merge annotations manually

If the auto-merge fails, manually combine the files:

```bash
python -c "
import pandas as pd
dfs = [pd.read_csv(f'data/annotations_annotator_{i}.csv') for i in [1,2,3]]
merged = pd.concat(dfs, ignore_index=True)
merged.to_csv('data/annotations.csv', index=False)
print('Merged successfully!')
"
```

---

## Notes

- **Blinded annotation:** Annotators should NOT see each other's judgments
- **No HH-RLHF labels:** The annotation interface hides original rejection reasons
- **Reproducibility:** The same 500 samples (stratified by length) are used across all annotators
- **Seed:** Fixed random seed (42) ensures reproducible sampling

---

*This is a research experiment requiring genuine human evaluation. Mock/synthetic data is not acceptable for publication.*
