# ICML 2025 Overleaf Project

## Paper Title
Can You Fine-Tune What a Model Cannot Do? Zero-Shot Evaluation as an Architectural Compatibility Gate for Parameter-Efficient Fine-Tuning

## Project Structure
```
overleaf/
├── main.tex                 # Main LaTeX document
├── icml2025.sty            # ICML 2025 style file
├── references.bib          # Bibliography (BibTeX format)
├── sections/               # Individual section files
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_related_work.tex
│   ├── 04_methodology.tex
│   ├── 05_experimental_setup.tex
│   ├── 06_results.tex
│   ├── 07_discussion.tex
│   └── 08_conclusion.tex
└── figures/                # Figure files
    ├── gate_metrics.png
    └── performance_table.png
```

## Compilation Instructions

### Local Compilation
```bash
cd overleaf
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Overleaf Upload
1. Create new project on Overleaf
2. Upload all files maintaining directory structure
3. Set compiler to pdfLaTeX
4. Compile (automatic on Overleaf)

## Citation Keys in BibTeX
- hu2021lora
- gu2023mamba
- wang2018glue
- li2021prefix
- lester2021prompt
- gu2022s4
- devlin2019bert
- radford2019gpt2
- raffel2020t5
- houlsby2019adapters
- katharopoulos2020linear
- peng2023rwkv
- poli2023hyena
- pan2010survey
- yosinski2014transferable
- ganin2016domain
- zamir2018taskonomy
- brown2020gpt3

## Notes
- ICML 2025 style file included (minimal functional version)
- All citations use natbib format
- Figures referenced as Fig~\ref{fig:gate_metrics}
- Tables use booktabs package
- Main document is camera-ready format
