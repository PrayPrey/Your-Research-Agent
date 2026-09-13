# Overleaf LaTeX Project

**Paper:** Alignment Fingerprinting: DPO and SFT Models Are Separable by Truthfulness, Not Fairness

**Format:** ICML 2025

## Files

- `main.tex` — main document
- `references.bib` — BibTeX references
- `sections/01_abstract.tex` through `sections/08_conclusion.tex` — section files
- `figures/` — all 7 paper figures (PNG)
- `icml2025.cls`, `icml2025.sty`, `icml2025.bst` — ICML 2025 style files

## Compilation

```bash
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Output: `main.pdf` (10 pages)

## Notes

- References compiled with natbib (icml2025 class includes natbib by default)
- "Float(s) lost" warning is non-fatal; figures may reflow slightly
- All figures are PNG at original resolution from paper/figures/
