# Baseline Results for Selected Nonlinear System Identification Benchmarks

## Key Metadata
- **Authors:** M.D. Champneys et al.
- **Year:** 2024  
- **Venue:** Preprint (arXiv)
- **Core Contribution:** Establishes objective baseline comparison methodology for nonlinear system identification by evaluating 10 techniques across 5 benchmarks, demonstrating method rankings vary by dataset.

## Section Summaries

### Abstract
Addresses challenge of choosing between competing nonlinear system identification models. While benchmark datasets enable objective comparison, meaningful inference requires understanding baseline performance from well-established methods. Presents 10 baseline techniques evaluated on 5 popular benchmarks to stimulate discussion regarding objective comparison of identification methodologies.

### Introduction & Motivation  
Nonlinear system identification (NLSI) remains open challenge with wide variety of techniques published annually. Question "which approach is best?" highly dependent on individual problem. Benchmark datasets (Silverbox, EMPS, Wiener-Hammerstein, Cascaded Tanks, Coupled Electric Drives) allow meaningful comparison, but isolated comparisons between models from single class (e.g., neural networks vs. other neural networks, neglecting linear baselines) undermine benchmark utility. Baseline results defend against this by providing well-established reference points across model classes.

### Methodology
**Benchmarks:** 5 SISO systems from nonlinearbenchmark.org - Silverbox (Duffing oscillator, n_x=2 states), EMPS (friction behavior, n_x=4), Wiener-Hammerstein (saturation nonlinearity between LTI blocks, n_x=6), Cascaded Tanks (overflow nonlinearities, n_x=2), Coupled Electric Drives (absolute velocity measurement, n_x=3).

**Baseline Techniques (10 models across 3 classes):**  
1. **State-Space Models:** LTI SS (discrete-time, prediction error framework, subspace initialization), Encoder-Decoder SS (nonlinear state update via MLP encoder h_ψ, linear measurement C·x_t), Full nonlinear SS (both state update and measurement nonlinear via MLPs).
2. **Auto-Regressive:** ARX (linear map from lagged I/O), NARX (polynomial nonlinearity via basis expansion Φ(·)), NARX-GP (Gaussian Process on Hankel matrix H), NARX-NN (feedforward neural network Φ_θ(H) with 3 hidden layers 64 neurons each).
3. **Recurrent Neural Networks:** LSTM (forget/input/output gates, 64 hidden units), GRU (reset/update gates, 64 hidden units), Vanilla RNN (tanh activation, 128 hidden units).

**Hyperparameters:** Lag structures (n_y, n_u) selected via AIC on validation set up to max 20 lags. State orders from benchmark descriptions. Mean-subtraction for LTI SS (Best Linear Approximation). Evaluation metric: free-running simulation MSE (only initial conditions observed, most rigorous test per Schoukens & Ljung 2019). All metrics in original coordinates (not normalized).

| Benchmark | n_y | n_u | Training Samples | Test Samples |
|-----------|-----|-----|-----------------|--------------|  
| Silverbox | 10 | 10 | 40,000 | 40,000 |
| W-H | 8 | 15 | 100,000 | 89,000 |
| EMPS | 16 | 5 | 188,000 | 100,000 |
| Cascaded Tanks | 9 | 8 | 44,750 | 43,400 |
| CED | 10 | 10 | 110,000 | 50,000 |

### Experiments & Results
**Key Finding:** Method rankings change dramatically across benchmarks - no universal winner.

| Benchmark | Best Method | Normalized MSE | 2nd Best | LTI SS (Linear Baseline) |
|-----------|-------------|---------------|----------|-------------------------|
| Silverbox | LSTM | 0.085 | Full-NL SS (0.092) | 0.142 |
| W-H | NARX-Poly | 0.032 | ARX (0.041) | 0.041 |  
| EMPS | GRU | 0.151 | LSTM (0.163) | 0.421 |
| Cascaded Tanks | Full-NL SS | 0.073 | LSTM (0.095) | 0.136 |
| CED | Encoder-Decoder SS | 0.228 | NARX-GP (0.235) | 0.312 |

**Observations:**  
- **Silverbox:** RNNs (LSTM/GRU) dominate, 40-67% better than LTI. Polynomial NARX underperforms (0.187 vs LSTM 0.085).
- **W-H:** Linear methods competitive (ARX 0.041 ties for 2nd). Polynomial NARX wins (0.032), exploiting known saturation structure. RNNs worse (LSTM 0.126, 3.9× worse than NARX-Poly).
- **EMPS:** RNNs excel (GRU 0.151), capturing friction dynamics. LTI SS poor (0.421, 2.8× worse). AR methods intermediate.
- **Cascaded Tanks:** Nonlinear SS best (0.073), RNNs strong (LSTM 0.095). Polynomial NARX fails (0.223, 3× worse than winner).  
- **CED:** State-space models lead (Encoder-Decoder 0.228). Output symmetry challenges AR methods. NARX-NN worst (0.452, 2× worse than winner).

**Variance Across Runs:** High variance observed for some methods (e.g., Full-NL SS on Silverbox: mean 0.092 ± std 0.045), indicating initialization sensitivity. LTI SS deterministic (subspace init).

### Discussion & Conclusion
Establishes that objective comparison requires breadth of baseline methods across model classes. Dataset characteristics determine which approach succeeds: Wiener-Hammerstein rewards exploitation of known structure (polynomial NARX), while EMPS/Silverbox favor flexibility (RNNs). Linear baselines (ARX, LTI SS) competitive on some benchmarks (W-H), highlighting that nonlinearity doesn't always justify complex models. Variability in rankings across benchmarks invalidates "one-size-fits-all" claims.  Recommendations: Always compare novel methods against diverse baselines (linear, polynomial, neural); report multiple runs with variance for stochastic methods; acknowledge dataset-specific performance trade-offs.

## Key Contributions  
- First systematic baseline study for NLSI across diverse model classes (SS, AR, RNN)
- Objective comparison methodology: free-running simulation MSE, consistent train/test splits, no dataset-specific tuning
- Empirical demonstration that method rankings are benchmark-dependent: LSTM wins Silverbox (0.085) but underperforms on W-H (0.126 vs NARX-Poly 0.032)
- Public Python data-loaders for reproducible benchmarking (github.com/GerbenBeintema/nonlinear_benchmarks)

## Potential Relevance  
Directly addresses "no single optimal method across dataset diversity" gap. Provides concrete evidence that baseline comparison methodology must span model classes to avoid biased conclusions. Demonstrates systematic investigation approach using existing benchmarks with automatic evaluation (simulation MSE, no human judgment). Lag structure selection via AIC illustrates dataset-aware hyperparameter tuning. Variance reporting highlights reliability considerations for stochastic methods. Benchmark results establish performance targets for fair comparison in future research.
