# DNSI Paper - Overleaf Project

## Structure
- `main.tex` - Main document
- `sections/` - Individual section files (00-07)
- `figures/` - PNG figures
- `references.bib` - Bibliography
- `icml2025.sty` - ICML 2025 style file

## Compilation
```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

## Upload to Overleaf
1. Create new project on Overleaf
2. Upload all files maintaining directory structure
3. Set main document to `main.tex`
