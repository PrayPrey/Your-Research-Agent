# Overleaf LaTeX Project

## Paper
**Emergence Uniformity Cannot Distinguish Spurious Features on Frozen Pretrained Representations**

## Compilation Instructions

### On Overleaf
1. Upload this entire folder to Overleaf
2. Download `icml2025.sty` from https://icml.cc/Conferences/2025/StyleAuthorInstructions
3. Upload the style file to the project root
4. Set main document to `main.tex`
5. Compile with pdfLaTeX

### Local Compilation
```bash
cd overleaf
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Project Structure
```
overleaf/
├── main.tex           # Main document
├── references.bib     # Bibliography
├── README.md          # This file
├── sections/          # Content sections
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
    ├── cv_distribution.png
    ├── gate_comparison.png
    ├── roc_curve.png
    └── trajectories.png
```

## Requirements
- ICML 2025 style files (`icml2025.sty`)
- pdfLaTeX with standard packages (graphicx, booktabs, natbib, etc.)

Generated: 2026-08-19
