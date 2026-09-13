# H-E2: GPU-normalized SAT Profiler

**Hypothesis**: GPU-normalized SAT (P95/Median batch time × GPU utilization fraction) causally predicts ≥15% epoch-time degradation with ≥80% precision when GPU utilization <90%.

## Quick Start

```bash
# Run the full experiment
./run_experiment.sh
```

## Project Structure

```
code/
├── src/
│   ├── profiling/       # SAT profiler implementation
│   ├── data/            # Dataset loaders with jitter injection
│   ├── models/          # Model loading (CNN + Transformer)
│   ├── experiment/      # Experiment orchestration
│   ├── evaluation/      # Metrics computation
│   ├── visualization/   # Figure generation
│   ├── config.py        # Configuration dataclasses
│   └── main.py          # Main execution script
├── requirements.txt     # Python dependencies
├── run_experiment.sh    # Experiment launcher
└── README.md            # This file
```

## Outputs

After running, check:
- `../results/profiling_results.json` - Per-config profiling data
- `../results/metrics_summary.json` - Gate validation metrics
- `../figures/*.png` - 6 visualization plots
- `experiment.log` - Execution log

## Gate Validation

**MUST_WORK Gate**:
- Precision ≥ 0.80
- Recall ≥ 0.70

Check `metrics_summary.json` for gate status.

## Implementation Notes

- **Reduced PoC**: 12 configs (6 CNN + 6 Transformer) instead of 48
- **Limited batches**: 100 batches per config for faster validation
- **GPU fallback**: Uses memory allocation as GPU utilization proxy (torch.cuda.utilization() unavailable)
- **Single seed**: seed=42 (sufficient for profiling validation)

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- 16GB GPU memory (minimum)
- ~50GB disk space for datasets
