# Overleaf LaTeX Project

## Compilation Instructions

```bash
cd overleaf
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Structure

- `main.tex` - Main document
- `sections/` - LaTeX section files (00-07)
- `figures/` - PNG figures
- `references.bib` - BibTeX bibliography

## Upload to Overleaf

1. Zip entire `overleaf/` folder
2. Upload to Overleaf as new project
3. Compile with pdflatex
