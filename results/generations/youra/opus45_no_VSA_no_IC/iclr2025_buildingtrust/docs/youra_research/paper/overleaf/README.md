# Overleaf LaTeX Project

Multi-Dimensional Truthfulness in LLMs: A Cross-Benchmark Correlation Study

## Structure

```
overleaf/
├── main.tex           # Main document
├── references.bib     # BibTeX references
├── sections/          # Section .tex files (00-08)
└── figures/           # PNG figures
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or use Overleaf's auto-compile.

## Requirements

- pdflatex (TeX Live 2020+)
- Standard packages: times, graphicx, booktabs, amsmath, hyperref, natbib
