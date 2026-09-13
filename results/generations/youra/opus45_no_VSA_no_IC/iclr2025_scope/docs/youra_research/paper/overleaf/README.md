# Overleaf Project: Sub-Linear Scaling Laws for Optimal LoRA Rank

## Structure

```
overleaf/
├── main.tex              # Main document
├── references.bib        # Bibliography
├── sections/             # LaTeX sections
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_experimental_setup.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   ├── 07_conclusion.tex
│   └── 08_figures.tex
└── figures/              # PNG figures
    ├── fig_1_entropy_correlation.png
    ├── fig_2_scaling_law.png
    ├── fig_3_task_comparison.png
    ├── fig_4_sensitivity.png
    └── fig_5_rank_curves.png
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Overleaf Upload

1. Zip this folder
2. Upload to Overleaf as new project
3. For ICML submission: replace preamble with official icml2025.sty
