# H-M3: Random Mathlib Tactic Sampling

Random tactic sampler testing corpus contribution hypothesis (18-25% success target, Δ=3-10pp vs lean-auto 15.6%).

## Quick Start

```bash
# Run full evaluation (244 problems, ~3h wall-clock)
./run_experiment.sh

# Results
cat results/h_m3_aggregate.yaml
```

## Components

- `src/random_sampler.py` - Weighted RNG from empirical Mathlib distribution
- `src/worker.py` - Per-problem evaluation
- `src/main.py` - Parallel harness (8 workers)
- `src/aggregate.py` - Statistical analysis (Wilson CI, z-test)
- `config/tactic_distribution.yaml` - Empirical weights

## Configuration

Edit `config/tactic_distribution.yaml` to change:
- Tactic distribution (weights must sum to 1.0)
- Budget (default: 15 evaluations)
- Timeout (default: 300s)
- Workers (default: 8)

## Reproducibility

Deterministic seeding: problem index → RNG seed

```bash
# Rerun 10% subset (should match exactly)
python src/main.py --minif2f-path ... --workers 1 --subset 0:24
```

## Gate Criteria (SHOULD_WORK)

- Success rate ∈ [18%, 25%]
- Δ vs lean-auto ∈ [3%, 10%] pp
- p < 0.05 (one-sided z-test)
