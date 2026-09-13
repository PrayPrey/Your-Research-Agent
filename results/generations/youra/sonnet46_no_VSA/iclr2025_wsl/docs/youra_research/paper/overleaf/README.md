# Overleaf LaTeX Project

**Paper:** Architectural Permutation-Invariance in Weight Encoders: Closing the OrbitVar → MSE_perm → R² Causal Chain

## Structure

```
overleaf/
├── main.tex              # Main document
├── references.bib        # BibTeX references
├── icml2025.sty          # ICML 2025 style file
├── icml2025.bst          # ICML 2025 bibliography style
├── sections/             # Section .tex files (00–07)
├── figures/              # All PNG figures
└── main.pdf              # Compiled output (9 pages)
```

## Compile

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Upload to Overleaf

Zip the entire `overleaf/` directory and upload via Overleaf → New Project → Upload Project.
