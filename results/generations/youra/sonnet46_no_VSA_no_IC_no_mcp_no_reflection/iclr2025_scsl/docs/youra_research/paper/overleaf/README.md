# Overleaf LaTeX Project

**Paper:** Gradient Alignment as Spurious-Minority Detector: An Empirical Negative Result and Mechanistic Diagnosis

## Compilation (local)

```bash
cd paper/overleaf
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Compilation (Overleaf)

1. Zip this folder: `zip -r overleaf_project.zip paper/overleaf/`
2. Upload zip to Overleaf (New Project → Upload Project)
3. Ensure compiler is set to **pdfLaTeX**
4. Download `icml2025.sty` from https://icml.cc/Conferences/2025/StyleAuthorInstructions and upload to root

## Structure

```
overleaf/
  main.tex              # Root document
  references.bib        # BibTeX bibliography
  sections/
    abstract.tex
    introduction.tex
    related_work.tex
    methodology.tex
    experiments.tex
    results.tex
    discussion.tex
    conclusion.tex
    appendix.tex
  figures/              # All paper figures (PNG)
  output.pdf            # Compiled PDF (after local build)
```

## Notes

- ICML 2025 style (`icml2025.sty`) is NOT included due to license. Download separately.
- Without `icml2025.sty`, compilation will fail. A fallback `article` class is used as base.
- All figure filenames match section references exactly.
