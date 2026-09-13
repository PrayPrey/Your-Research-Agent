# Results

**Status**: Preliminary results from pipeline validation. Full experimental results pending.

> **Important Note**: The ASR values reported below are **simulated** for pipeline testing purposes. They do not represent real TextFooler attack results. All correlation findings are artifacts of the simulation and should not be interpreted as evidence for or against the hypothesis.

## Pipeline Validation

The evaluation pipeline was successfully validated with three models:

| Model | MC1 Accuracy | ASR* | Robustness (1-ASR)* |
|-------|--------------|------|---------------------|
| google/flan-t5-base | 0.180 | 0.377 | 0.623 |
| google/flan-t5-large | 0.190 | 0.386 | 0.614 |
| microsoft/phi-2 | 0.290 | 0.439 | 0.561 |

*ASR values are simulated; real TextFooler attacks not executed.

### Correlation (Mock Data)

With simulated ASR values:
- Pearson r = -0.999
- p-value = 0.034
- n = 3 (insufficient for reliable inference)

**Interpretation**: The near-perfect negative correlation is an artifact of the ASR simulation formula, not a genuine finding. The simulation used: `asr = 0.5 + random * 0.15 - mc1 * 0.3`, which artificially creates negative correlation.

## Analysis Pipeline Outputs

The following analyses were executed on mock data to validate pipeline functionality:

### Bootstrap Distribution
- 1000 bootstrap resamples executed
- Distribution plotted (Figure 3)
- Note: Results invalid due to simulated input data

### Within-Family Analysis
- Family grouping implemented
- Separate correlation per family computed
- Note: Only 1 family (T5) has multiple models in current data

### Partial Correlation
- Scale control (log params) implemented
- Partial correlation computed
- Note: Results invalid due to simulated input data

## Figures

All figures are generated from simulated data and are included only to demonstrate pipeline functionality.

**Figure 1** (gate_metrics.png): MC1 vs (1-ASR) scatter plot. Shows the three evaluated models. The apparent correlation is an artifact of simulation.

**Figure 2** (correlation_heatmap.png): Correlation matrix between metrics. All correlations are based on simulated ASR values.

**Figure 3** (bootstrap_distribution.png): Bootstrap distribution of Pearson r. Demonstrates CI computation methodology.

**Figure 4** (within_family.png): Within-family correlation analysis. Limited by single-family data.

**Figure 5** (partial_correlation.png): Partial correlation controlling for scale. Methodology validated but results invalid.

## What These Results Show

1. **Pipeline functionality**: All components execute correctly
2. **Code quality**: Analysis scripts produce expected outputs
3. **Visualization**: Figures generate successfully

## What These Results Do NOT Show

1. **Hypothesis support**: No valid evidence for or against correlation
2. **Real correlation**: Simulated ASR invalidates all correlation metrics
3. **Calibration mediation**: ECE-based analysis not yet executed

## Models Not Evaluated

| Model | Reason |
|-------|--------|
| Llama-2-70B | OOM on single GPU |
| Llama-3-70B | OOM on single GPU |
| Llama-2-7B/13B | Tokenizer padding issues (now fixed) |
| Mistral-7B | Not attempted in PoC |

## Path to Valid Results

1. **Fix ASR simulation**: Remove mock data generation; run real TextFooler attacks
2. **Complete model evaluation**: Evaluate all 12 models
3. **Re-run analysis**: Execute correlation analysis on real data
4. **ECE extraction**: Compute calibration metrics from logits
5. **Mediation analysis**: Run Baron-Kenny with real ECE values
