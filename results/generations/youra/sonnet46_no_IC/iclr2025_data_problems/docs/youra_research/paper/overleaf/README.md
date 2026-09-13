# Overleaf LaTeX Project

Paper: "One Size Does Not Fit All: Scale-Dependent Optimal Perplexity Filtering for Language Model Pre-training"

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Structure

- `main.tex` — root document
- `icml2025.sty` — ICML 2025 style file
- `references.bib` — BibTeX bibliography
- `sections/` — one .tex file per section (00–08)
- `figures/` — PNG figures (fig1–fig4)

## Requirements

- TeX Live 2020+ with `pdflatex` and `bibtex`
- Packages: `amsmath`, `amssymb`, `booktabs`, `graphicx`, `hyperref`, `microtype`
