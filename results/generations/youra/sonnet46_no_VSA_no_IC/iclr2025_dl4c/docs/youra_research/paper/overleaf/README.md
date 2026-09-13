# Overleaf LaTeX Project

**Paper:** When the Signal is Real but the Training is Not: Variance-Guided RLEF Data Selection and the Cold-Start Problem

**Format:** ICML 2025

**Generated:** 2026-08-21 by Anonymous Research Pipeline (Phase 6.5.1)

## Quick Start (Overleaf)

1. Upload this entire `overleaf/` folder to a new Overleaf project
2. Set `main.tex` as the main document
3. Set compiler to **pdfLaTeX**
4. Compile (Overleaf will run BibTeX automatically)

## Local Compilation

```bash
cd paper/overleaf/
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
# Output: main.pdf / output.pdf
```

## Project Structure

```
overleaf/
├── main.tex              # Main document
├── references.bib        # BibTeX references
├── icml2025.sty          # ICML 2025 style
├── icml2025.bst          # ICML 2025 bibliography style
├── sections/
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── methodology.tex
│   ├── experiments.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── conclusion.tex
│   └── appendix.tex
└── figures/              # All paper figures

```

## Checklist Before Submission

- [ ] Replace author information placeholders in `main.tex`
- [ ] Add institution affiliations
- [ ] Add acknowledgements section
- [ ] Verify all figure references compile correctly
- [ ] Check all citation keys resolve in bibliography
- [ ] Final proofread in Overleaf
- [ ] Verify page count within ICML limits
```
