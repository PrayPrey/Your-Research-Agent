# Overleaf LaTeX Project

## Paper
When Reward Granularity Matters: Mechanistic Analysis of Ratio vs. Binary Reward in GRPO Post-Training for Code LLMs

*Anonymous Submission — ICML 2025*

## Structure
```
overleaf/
├── main.tex              # Main document
├── references.bib        # BibTeX references
├── icml2025.sty          # ICML 2025 style
├── icml2025.bst          # ICML 2025 bibliography style
├── algorithmic.sty
├── algorithm.sty
├── sections/
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related.tex
│   ├── 03_methodology.tex
│   ├── 04_setup.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   └── 07_conclusion.tex
└── figures/
    ├── reward_histograms.png
    ├── mean_reward.png
    └── grad_norm_trajectory.png
```

## Compilation

```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`

## Overleaf Upload

1. Zip the entire `overleaf/` directory
2. Upload to Overleaf as a new project
3. Set compiler to pdfLaTeX
4. Click Compile
