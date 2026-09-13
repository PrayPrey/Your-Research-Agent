# Overleaf LaTeX Project

**Paper:** Spurious Features Dominate Through Convergence Speed, Not Gradient Competition: An Empirical Falsification

**Format:** ICML 2025

## Compilation Instructions

### Option 1: Overleaf (Recommended)
1. Upload this entire folder to Overleaf
2. Download `icml2025.sty` from https://icml.cc/Conferences/2025/StyleAuthorInstructions
3. Upload `icml2025.sty` to the project root
4. Set compiler to pdfLaTeX
5. Compile `main.tex`

### Option 2: Local Compilation
```bash
# Ensure icml2025.sty is in the directory
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Project Structure
```
overleaf/
├── main.tex              # Main document
├── references.bib        # Bibliography
├── README.md             # This file
├── sections/
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── methodology.tex
│   ├── experiments.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── conclusion.tex
│   └── appendix.tex
└── figures/
    ├── gate_bar_chart.png
    ├── gate_comparison.png
    ├── norm_comparison.png
    ├── ratio_over_epochs.png
    └── ratio_trajectory.png
```

## Requirements
- ICML 2025 style file (`icml2025.sty`)
- pdfLaTeX compiler
- BibTeX for references

---
*Generated: 2026-08-28 | Anonymous Research Pipeline*
