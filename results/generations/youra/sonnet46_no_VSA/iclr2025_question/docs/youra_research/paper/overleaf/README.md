# Overleaf LaTeX Project

**Paper:** Near-Orthogonal Uncertainty Signals: Empirical Independence of Semantic Entropy and Minimum Log-Probability for LLM Hallucination Detection

**Format:** ICML 2025

## Compilation

```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## File Structure

```
main.tex               - Main document
references.bib         - BibTeX references
icml2025.sty           - ICML 2025 style file
icml2025.bst           - ICML 2025 bibliography style
sections/
  abstract.tex
  introduction.tex
  related_work.tex
  methodology.tex
  experiments.tex
  results.tex
  discussion.tex
  conclusion.tex
  appendix.tex
figures/
  scatter_se_vs_minlogprob.png
  correlation_heatmap.png
  gate_metrics.png
  lr_coefficients.png
```

## Overleaf Upload

1. Zip this entire folder
2. Upload to Overleaf as new project
3. Set compiler to pdfLaTeX
4. Compile
