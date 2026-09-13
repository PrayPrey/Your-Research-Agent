# Overleaf Project: Orthogonal Uncertainty Signals for LLM Hallucination Detection

## Upload Instructions

1. Create new project on Overleaf
2. Upload all files maintaining this structure:
   ```
   main.tex
   references.bib
   sections/
     01_abstract.tex
     02_introduction.tex
     03_related.tex
     04_methodology.tex
     05_experiments.tex
     06_results.tex
     07_discussion.tex
     08_conclusion.tex
     09_appendix.tex
   figures/
     scatter_entropy_consistency.png
     distribution_comparison.png
     quadrant_analysis.png
     histogram_overlay.png
   ```
3. Set main document to `main.tex`
4. Compile with pdfLaTeX + BibTeX

## Local Compilation

```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

## Generated

Auto-generated from 06_paper_final.md by Phase 6.5.1 pipeline.
