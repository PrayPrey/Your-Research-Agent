# Overleaf LaTeX Project

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Structure

- `main.tex` - Main document
- `references.bib` - BibTeX references
- `sections/` - LaTeX section files (00-08)
- `figures/` - Paper figures

## Requirements

- pdflatex (TeX Live 2020+)
- natbib package
- booktabs package
