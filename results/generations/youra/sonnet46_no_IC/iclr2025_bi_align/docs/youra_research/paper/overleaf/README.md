# Overleaf LaTeX Project

**Paper**: Capability or Verbosity? Disentangling the Drivers of Length-Debiased Preference in LLM Evaluation

## Compilation

```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`

## Structure

```
overleaf/
├── main.tex              # Root document
├── references.bib        # BibTeX references
├── icml2025.sty          # ICML 2025 style
├── icml2025.bst          # ICML 2025 bibliography style
├── algorithm.sty
├── algorithmic.sty
├── sections/
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_experiments.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   ├── 07_conclusion.tex
│   └── 08_acknowledgments.tex
└── figures/              # 23 PNG figures
```

## Notes

- Anonymous submission format (author info omitted)
- ICML 2025 style files sourced from ai-scientist blank template
- Bibliography: 9 references (7 verified via Semantic Scholar)
