# Overleaf LaTeX Project

**Paper:** Community Breadth Diversity Does Not Predict Benchmark Displacement: A Pre-Validated Null Result  
**Generated:** 2026-08-03 by YouRA Phase 6.5.1

## Compilation Instructions

### On Overleaf
1. Upload this entire folder to a new Overleaf project
2. Download `icml2025.sty` from https://icml.cc/Conferences/2025/StyleAuthorInstructions and upload to the project root
3. Set compiler to **pdfLaTeX**
4. Set main document to `main.tex`
5. Click Compile

### Local Compilation (without icml2025.sty)
```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Project Structure
```
overleaf/
├── main.tex                  # Main document
├── references.bib            # BibTeX references
├── README.md                 # This file
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
└── figures/                  # Place figure files here
```

## Notes
- `icml2025.sty` not included (download separately per ICML instructions)
- Unverified references in `references.bib` marked with `[UNVERIFIED]` — verify before submission
- Figures referenced in appendix are in the research pipeline archive (`h-e1/figures/`, `h-m1/figures/`)
