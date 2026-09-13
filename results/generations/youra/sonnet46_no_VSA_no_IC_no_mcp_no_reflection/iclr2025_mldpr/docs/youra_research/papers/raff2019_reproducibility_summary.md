# Paper Summary: A Step Toward Quantifying Independently Reproducible ML Research
**Authors:** Edward Raff | **Year:** 2019 | **arXiv:** 1909.06674

## Overview
Raff conducted the first large-scale empirical audit of ML paper reproducibility, attempting to re-implement 255 papers from top ML venues (NeurIPS, ICML, ICLR, JMLR) from scratch and recording binary success/failure outcomes.

## Key Contributions
- Ground-truth binary reproducibility labels for 255 papers (50.8% reproducible)
- Identified factors correlated with reproducibility: pseudocode presence, equation count, hyperparameter reporting, dataset accessibility
- Found no single dominant factor — reproducibility is multifactorial

## Methodology
- Single researcher (Raff) re-implemented each paper over ~1 week
- Binary outcome: reproducible (close to reported results) vs. not
- Logistic regression on ~60 features extracted per paper

## Experiments & Results
- Reproducibility rate: 50.8% (129/255 papers)
- Significant positive predictors: explicit hyperparameter reporting, pseudocode, reference implementation availability
- Significant negative predictors: complexity of required compute, custom evaluation metrics
- Dataset misuse / out-of-context application not explicitly measured — this is a gap

## Relevance to Gap 2
Raff's dataset provides the most comprehensive labeled reproducibility outcomes available.
The key missing link: his feature set covers algorithm reporting completeness but NOT
dataset usage appropriateness (task-type fit, documentation completeness, concentration).
Our hypothesis: adding metadata-observable misuse signals as features would improve
reproducibility prediction, and the signals themselves would show significant correlation.

## Limitations for Our Study
- Single-annotator bias (one researcher's assessment)
- Papers from 2013-2018 (vintage bias)
- Binary outcome loses failure severity information
- Dataset metadata not collected at time of evaluation
