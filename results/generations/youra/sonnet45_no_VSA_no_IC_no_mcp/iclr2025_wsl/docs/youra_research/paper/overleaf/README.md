# Overleaf LaTeX Project

## Compilation

Compile with pdflatex + bibtex:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Structure

- `main.tex` - Main document
- `sections/` - Individual LaTeX section files (01-09)
- `figures/` - PNG figures
- `references.bib` - BibTeX bibliography
- `icml2025.sty` - ICML 2025 style file

## Upload to Overleaf

1. Create new Overleaf project
2. Upload all files from this directory
3. Set main document to `main.tex`
4. Compile with pdfLaTeX
