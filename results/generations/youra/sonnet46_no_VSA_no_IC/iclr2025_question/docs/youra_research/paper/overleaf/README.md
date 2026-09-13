# Overleaf LaTeX Project

**Paper:** Hallucination Type Determines Optimal Token Log-Probability Aggregation: A Mechanism-Grounded Ablation  
**Format:** ICML 2025  
**Generated:** 2026-08-21 by Anonymous Research Pipeline (Phase 6.5.1)

## Structure

```
overleaf/
├── main.tex              # Root document
├── references.bib        # BibTeX references (13 entries, 10 verified)
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
└── figures/              # 27 PNG figures
```

## Compilation

### Local (requires TeX Live with ICML 2025 style)

1. Download `icml2025.sty` from https://icml.cc/Conferences/2025/StyleAuthorInstructions
2. Place in this directory
3. Run:
   ```bash
   pdflatex main.tex
   bibtex main
   pdflatex main.tex
   pdflatex main.tex
   ```

### Overleaf

1. Create new project → Upload ZIP
2. ZIP the entire `overleaf/` folder contents
3. Upload and set compiler to **pdfLaTeX**
4. Overleaf will prompt to install `icml2025` package automatically, or upload `icml2025.sty` manually

## Notes

- Three arXiv preprint citations (Ma2025, Moslonka2025, Zhang2025) should be verified against published versions before submission
- NQ dataset results pending (GPU time only required)
- AUROC cross-pipeline comparisons should be interpreted with caution (see Section 6.3)
