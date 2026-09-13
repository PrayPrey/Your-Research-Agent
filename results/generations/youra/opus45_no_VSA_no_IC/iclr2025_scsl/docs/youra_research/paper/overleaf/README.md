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
- `references.bib` - Bibliography
- `sections/` - LaTeX section files (00-07)
- `figures/` - PNG figures

## Overleaf Upload

1. Create new project on Overleaf
2. Upload all files maintaining directory structure
3. Set `main.tex` as main document
4. Compile with pdfLaTeX + Bibtex
