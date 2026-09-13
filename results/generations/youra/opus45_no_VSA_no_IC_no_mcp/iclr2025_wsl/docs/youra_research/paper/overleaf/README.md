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
- `sections/` - Section files (00-08)
- `figures/` - PNG figures
- `references.bib` - BibTeX references

## Upload to Overleaf

1. Zip entire `overleaf/` folder
2. Create new Overleaf project from zip
3. Compile with pdflatex
