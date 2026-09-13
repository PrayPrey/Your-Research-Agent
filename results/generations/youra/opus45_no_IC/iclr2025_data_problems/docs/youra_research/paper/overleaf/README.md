# Overleaf LaTeX Project

**Paper:** Quantifying Benchmark Contamination: A Transfer Function Approach

**Target:** ICML 2025

## Quick Start

1. Upload this entire folder to Overleaf
2. Download `icml2025.sty` from https://icml.cc/Conferences/2025/StyleAuthorInstructions
3. Upload `icml2025.sty` to the project root
4. Set compiler to pdfLaTeX
5. Compile `main.tex`

## Local Compilation

```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Structure

```
overleaf/
├── main.tex           # Main document
├── references.bib     # Bibliography
├── README.md          # This file
├── sections/          # LaTeX sections
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── methodology.tex
│   ├── experiments.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── conclusion.tex
│   └── appendix.tex
└── figures/           # Paper figures
    ├── capability_detrending.png
    ├── checkpoint_trajectory.png
    ├── comparison_prior_work.png
    ├── contamination_by_benchmark.png
    ├── gate_scatter.png
    ├── overlap_by_benchmark.png
    ├── overlap_histograms.png
    └── residual_distribution.png
```

## Note

This project requires ICML 2025 style files (`icml2025.sty`) which must be obtained from the official ICML website due to licensing.

Generated: 2026-08-10
