# Overleaf LaTeX Project: Budget-Aware UQ for LLM Selective Prediction

This directory contains a ready-to-compile LaTeX paper converted from `06_paper_final.md`.

## Structure

```
overleaf/
├── main.tex                # Main LaTeX document
├── references.bib          # Bibliography (copied from 06_references.bib)
├── icml2025.sty           # ICML 2025 style file
├── fancyhdr.sty           # Required by ICML style
├── sections/               # Individual section files (8 total)
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── methodology.tex
│   ├── experiments.tex
│   ├── results.tex
│   ├── discussion.tex
│   └── conclusion.tex
└── figures/                # All PNG figures from paper/figures/
    ├── auroc_comparison.png
    ├── ause_vs_auroc.png
    ├── gate_metrics_scatter.png
    ├── roc_curves.png
    ├── sparsification_curves.png
    ├── spearman_comparison.png
    └── uncertainty_distributions.png
```

## Local Compilation

```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The final PDF will be `main.pdf` (or `output.pdf` if renamed).

## Uploading to Overleaf

1. Create a new blank project on Overleaf
2. Upload all files from this directory (main.tex, sections/, figures/, references.bib, *.sty)
3. Set the compiler to pdfLaTeX (Project Settings → Compiler)
4. Compile

## Customization

- **Title/Authors:** Edit the `\icmltitle{}` and `\icmlauthorlist` blocks in `main.tex`
- **Affiliations:** Modify `\icmlaffiliation{inst}{...}` in `main.tex`
- **Contact email:** Update `\icmlcorrespondingauthor{...}{...}` in `main.tex`
- **Content edits:** Modify individual section files in `sections/`

## Citation Keys

All references use lowercase kebab-case keys matching the markdown version:
- `\cite{guo2017calibration}` → Guo et al. 2017
- `\cite{gal2016dropout}` → Gal & Ghahramani 2016
- `\cite{lin2021truthfulqa}` → Lin et al. 2021 (TruthfulQA)
- `\cite{su2024conformal}` → Su et al. 2024 (conformal prediction)
- etc.

## Known Issues

- Author name/affiliation placeholders need manual update
- Figure captions use relative paths (`figures/*.png`) — works in Overleaf, verify locally
- Some special characters ($\times$, $\geq$, etc.) are already escaped for LaTeX
- Tables use `booktabs` package (already loaded in preamble)

## Verification Checklist

- [ ] Update author name, affiliation, email in `main.tex`
- [ ] Verify all 7 figures render correctly
- [ ] Check bibliography compiles (no missing citations)
- [ ] Proofread for LaTeX escape issues (%, &, $, #, etc.)
- [ ] Confirm page limit compliance (ICML 2025: 8 pages + unlimited references)
