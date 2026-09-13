# Overleaf Project: Batch Normalization Amplifies Worst-Group Gaps

## Structure

```
overleaf/
├── main.tex                 # Main LaTeX document
├── icml2025.sty             # ICML 2025 style file
├── references.bib           # Bibliography
├── sections/
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_related_work.tex
│   ├── 04_methodology.tex
│   ├── 05_experimental_setup.tex
│   ├── 06_results.tex
│   ├── 07_discussion.tex
│   └── 08_conclusion.tex
└── figures/
    └── (figure files)
```

## Compilation

Local compilation:

```bash
cd overleaf
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`

## Upload to Overleaf

1. Create new Overleaf project (blank template)
2. Upload all files from `overleaf/` directory:
   - `main.tex`
   - `icml2025.sty`
   - `references.bib`
   - All files in `sections/`
   - All files in `figures/`
3. Set main document to `main.tex`
4. Compile

## Paper Metadata

- **Conference**: ICML 2025
- **Style**: icml2025.sty
- **Author**: Anonymous (for review)
- **Sections**: 8 (Abstract, Introduction, Related Work, Methodology, Experimental Setup, Results, Discussion, Conclusion)
- **Tables**: 3 (RQ1 gaps, RQ2 gradients, RQ3 consistency)
- **Figures**: None (proof-of-concept on synthetic data)
- **References**: 15 citations

## Key Results

- **RQ1**: BN shows 9.41pp higher worst-group gap than LN at 90% average accuracy (*p* < 0.001, *d* = 3.94)
- **RQ2**: BN shows 26% higher gradient ratio (majority/minority) during early training (*p* < 0.001, *d* = 4.32)
- **RQ3**: Perfect ranking correlation (ρ = 1.0) on synthetic datasets (requires real dataset validation)

## Limitations

1. **Synthetic data only** — real Waterbirds/CelebA validation pending
2. **Attention hypothesis incomplete** — ViT/CBAM deferred to future work
3. **Vision tasks only** — NLP/audio/tabular generalization untested
4. **Constant learning rate** — LR schedule ablation pending

## Citation

```bibtex
@inproceedings{anonymous2025batchnorm,
  title={Batch Normalization Amplifies Worst-Group Accuracy Gaps via Gradient-Level Mechanisms During Early Training},
  author={Anonymous},
  booktitle={Proceedings of the 42nd International Conference on Machine Learning},
  year={2025}
}
```
