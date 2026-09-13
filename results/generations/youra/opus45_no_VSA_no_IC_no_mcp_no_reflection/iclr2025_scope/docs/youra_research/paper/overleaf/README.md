# Overleaf LaTeX Project

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or upload to Overleaf for online compilation.

## Structure

- `main.tex` - Main document
- `sections/` - Paper sections (00-08)
- `figures/` - PNG figures
- `references.bib` - Bibliography

## Requirements

- ICML 2025 style files (icml2025.sty, icml2025.bst)
- pdflatex, bibtex
