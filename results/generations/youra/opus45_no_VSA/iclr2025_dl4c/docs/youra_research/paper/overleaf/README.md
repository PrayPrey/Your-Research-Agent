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
- `references.bib` - BibTeX references
- `sections/` - LaTeX section files (00-08)
- `figures/` - Paper figures

## Note

For ICML 2025 submission, add style files and uncomment `\usepackage{icml2025}` in main.tex.
