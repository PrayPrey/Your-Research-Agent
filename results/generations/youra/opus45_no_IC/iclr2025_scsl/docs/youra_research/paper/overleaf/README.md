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
- `sections/` - Individual section files (00-08)
- `figures/` - Figure files (PNG)
- `references.bib` - BibTeX references

## Overleaf Upload

1. Create new project on Overleaf
2. Upload all files maintaining folder structure
3. Set main.tex as main document
4. Compile with pdfLaTeX + BibTeX
