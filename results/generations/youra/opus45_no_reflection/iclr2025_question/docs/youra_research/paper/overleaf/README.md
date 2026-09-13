# Overleaf LaTeX Project

## Compilation Instructions

To compile this document:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Project Structure

- `main.tex` - Main document
- `references.bib` - Bibliography
- `sections/` - Individual section files
  - `00_abstract.tex`
  - `01_introduction.tex`
  - `02_related_work.tex`
  - `03_methodology.tex`
  - `04_experiments.tex`
  - `05_results.tex`
  - `06_discussion.tex`
  - `07_conclusion.tex`
- `figures/` - Figure files

## Requirements

- pdflatex
- bibtex
- Standard LaTeX packages: times, latexsym, graphicx, amsmath, amssymb, booktabs, hyperref, natbib
