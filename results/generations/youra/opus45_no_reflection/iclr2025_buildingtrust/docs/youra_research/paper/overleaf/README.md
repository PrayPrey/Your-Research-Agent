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
- `sections/` - Section files (00-07)
- `figures/` - Paper figures
- `references.bib` - Bibliography

## Requirements

- pdflatex
- bibtex
- booktabs package
