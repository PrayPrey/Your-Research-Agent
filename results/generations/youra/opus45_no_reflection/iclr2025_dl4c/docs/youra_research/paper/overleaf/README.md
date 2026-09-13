# Overleaf LaTeX Project

## Compilation

```bash
cd overleaf
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Structure

- `main.tex` - Main document
- `references.bib` - Bibliography
- `sections/` - Individual section files
- `figures/` - Figure files (if any)

## Requirements

- pdflatex
- bibtex
- natbib package
