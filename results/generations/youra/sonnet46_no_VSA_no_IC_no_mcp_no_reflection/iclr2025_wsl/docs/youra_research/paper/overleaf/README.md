# Overleaf LaTeX Project

**Paper:** Can Weight-Space Encoders Predict Generalization Gap? A Controlled Study of Equivariant Architectures

## Structure

```
overleaf/
├── main.tex              # Root document
├── references.bib        # BibTeX references
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
├── figures/              # All PNG figures
└── output.pdf            # Compiled PDF (after build)
```

## Compile

```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Overleaf Upload

1. Zip this folder
2. Upload to Overleaf as new project
3. Set compiler to pdfLaTeX
4. For ICML 2025 style: add `icml2025.sty` and update `\documentclass` accordingly
