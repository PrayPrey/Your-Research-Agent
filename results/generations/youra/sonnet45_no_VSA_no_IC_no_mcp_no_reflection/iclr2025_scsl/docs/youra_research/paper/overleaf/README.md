# Overleaf LaTeX Project: Temporal Ordering Paper

## Structure

- `main.tex` - Main document entry point
- `sections/` - Individual LaTeX sections (01-08)
  - `01_abstract.tex`
  - `02_introduction.tex`
  - `03_related.tex`
  - `04_methodology.tex`
  - `05_setup.tex`
  - `06_results.tex`
  - `07_discussion.tex`
  - `08_conclusion.tex`
- `figures/` - All figures referenced in paper
- `references.bib` - BibTeX bibliography

## Compilation

### Local compilation (requires pdflatex, bibtex):

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`

### Overleaf

1. Zip entire `overleaf/` directory
2. Upload to Overleaf as new project
3. Set compiler to pdfLaTeX
4. Compile (automatic in Overleaf)

## Figures

All figures generated from Phase 4/Phase 5 validation experiments:
- `convergence_comparison.png` - h-e1 temporal gap validation
- `temporal_gap_distribution.png` - Multi-seed gap distribution
- `layer_correlation_means.png` - h-m1 layer-wise mechanism
- `neuron_correlation_heatmap.png` - Per-neuron correlation
- `gate_metrics.png` - h-c1 intervention failure
- `correlation_cdf.png` - Correlation CDF analysis
- `rolling_variance.png` - h-e2 variance metric
- `R_temporal_vs_epoch.png` - h-e3 GradCAM ratio

## Generated

Auto-generated from `06_paper_final.md` via Phase 6.5.1 Overleaf conversion script.
Date: 2026-08-29
