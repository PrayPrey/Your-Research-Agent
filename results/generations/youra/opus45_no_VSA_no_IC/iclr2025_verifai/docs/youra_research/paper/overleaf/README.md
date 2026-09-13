# Overleaf LaTeX Project

**Paper:** Static Analysis Metrics Predict LLM Code Correctness: A Quantified Correlation Study

## Compilation

```bash
cd overleaf
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or use latexmk:
```bash
latexmk -pdf main.tex
```

## Structure

- `main.tex` - Main document
- `references.bib` - BibTeX references
- `sections/` - Section files (00-08)
- `figures/` - Figure files

## Overleaf Upload

1. Create new Overleaf project
2. Upload all files maintaining folder structure
3. Set main document to `main.tex`
4. Compile

## Notes

- Uses plainnat bibliography style (natbib compatible)
- ICML 2025 style file can be added if available
- All figures in PNG format
