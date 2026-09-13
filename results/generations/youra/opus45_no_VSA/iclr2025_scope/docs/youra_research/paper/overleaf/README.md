# IPCR Paper - Overleaf LaTeX Project

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
- `sections/` - Section files (01-09)
- `figures/` - PNG figures

## Notes

- Uses plainnat bibliography style
- Requires: booktabs, amsmath, graphicx, pifont
- For ICML submission: replace with icml2025.sty
