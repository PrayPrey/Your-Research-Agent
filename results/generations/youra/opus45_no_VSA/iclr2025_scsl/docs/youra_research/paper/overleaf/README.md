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
- `sections/*.tex` - Paper sections
- `references.bib` - Bibliography
- `figures/` - Figures (if any)

## Upload to Overleaf

1. Zip this folder
2. New Project → Upload Project
3. Compile
