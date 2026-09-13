# Overleaf LaTeX Project

## Compilation Instructions

### Local Compilation
```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Overleaf
1. Upload entire `overleaf/` folder to Overleaf
2. Download ICML 2025 style files from https://icml.cc/Conferences/2025/StyleAuthorInstructions
3. Upload `icml2025.sty` and related files to project root
4. Set main document to `main.tex`
5. Compile with pdfLaTeX

## Project Structure
```
overleaf/
├── main.tex           # Main document
├── references.bib     # Bibliography
├── README.md          # This file
├── sections/          # Paper sections
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── methodology.tex
│   ├── experiments.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── conclusion.tex
│   └── appendix.tex
└── figures/           # Figure files
    ├── alignment_bar.png
    ├── alignment_evolution.png
    └── svd_variance.png
```

## Notes
- ICML 2025 style file required for proper formatting
- Without style file, document compiles with fallback formatting
- All figures included as PNG format
