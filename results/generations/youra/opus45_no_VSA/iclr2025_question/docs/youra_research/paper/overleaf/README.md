# CLTI Paper - Overleaf Project

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Structure

- `main.tex` - Main document
- `references.bib` - Bibliography
- `sections/` - LaTeX section files (00-06)
- `figures/` - Paper figures

## Requirements

- pdflatex
- bibtex
- ICML 2025 style files (icml2025.sty)

## Overleaf Upload

1. Upload entire folder to Overleaf
2. Set main.tex as main document
3. Compile with pdfLaTeX
