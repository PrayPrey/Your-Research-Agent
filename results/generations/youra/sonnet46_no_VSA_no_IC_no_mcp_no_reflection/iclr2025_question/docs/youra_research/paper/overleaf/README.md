# Overleaf Project — ICML 2025

**Paper:** When Consistency Is Not Uncertainty: Sampling-Based Hallucination Detection Fails Under Systematic Confabulation in Instruction-Tuned LLMs

## Structure

```
overleaf/
  main.tex              # Root document
  icml2025.sty          # ICML 2025 style
  icml2025.bst          # BibTeX style
  references.bib        # Bibliography
  sections/
    abstract.tex
    introduction.tex
    related_work.tex
    methodology.tex
    experimental_setup.tex
    results.tex
    discussion.tex
    conclusion.tex
  figures/
    auroc_comparison.png
    roc_curves.png
    smc_nli_distribution.png
    nli_vs_embed_scatter.png
```

## Compile

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf` (8 pages)
