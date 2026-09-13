# Overleaf LaTeX Project

**Paper:** Specification-Aligned Repair for EvalPlus Semantic Failures: Data Infrastructure and Pre-Registered Design

**Generated:** 2026-08-22 by YouRA Anonymous Research Pipeline v1.0

---

## Quick Start (Overleaf)

1. Upload this entire `overleaf/` folder to a new Overleaf project
2. Set `main.tex` as the main document
3. Set compiler to **pdfLaTeX**
4. Compile: BibTeX → pdfLaTeX → pdfLaTeX

## Local Compilation

```bash
cd paper/overleaf/
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

## Project Structure

```
overleaf/
├── main.tex               # Main document
├── references.bib         # BibTeX references (11 entries)
├── icml2025.sty           # ICML 2025 style file
├── icml2025.bst           # ICML 2025 bibliography style
├── algorithm.sty
├── algorithmic.sty
├── fancyhdr.sty
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
├── figures/
│   ├── failure_distribution.png
│   ├── gate_conditions.png
│   ├── gate_metrics.png
│   ├── failing_tests_histogram.png
│   └── completeness_matrix.png
└── output.pdf             # Compiled PDF (if local compilation succeeded)
```

## Checklist Before Submission

- [ ] Replace author name placeholders in `main.tex`
- [ ] Replace institution placeholders in `main.tex`
- [ ] Replace email placeholders in `main.tex`
- [ ] Add acknowledgements section if needed
- [ ] Review `065_human_review_notes.md` for minor fixes
- [ ] Final quality check in Overleaf
- [ ] Verify all citations resolve correctly
- [ ] Check page count meets venue limits
