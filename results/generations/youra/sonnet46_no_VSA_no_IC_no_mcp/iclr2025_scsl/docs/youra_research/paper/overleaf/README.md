# Overleaf LaTeX Project

## Paper
Pretraining Paradigm Determines Spurious Feature Encoding: Supervised Label Correlation Dominates Augmentation Invariance

## Compilation Instructions

### Local (command line)
```bash
cd overleaf/
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

### Overleaf
1. Upload this entire folder as a zip to Overleaf
2. Set compiler to pdfLaTeX
3. Set main file to main.tex
4. Click Compile

## Structure
- main.tex — master document
- references.bib — BibTeX references
- icml2025.sty — ICML 2025 style file
- icml2025.bst — ICML 2025 bibliography style
- sections/ — individual section .tex files
- figures/ — all paper figures (PNG)
