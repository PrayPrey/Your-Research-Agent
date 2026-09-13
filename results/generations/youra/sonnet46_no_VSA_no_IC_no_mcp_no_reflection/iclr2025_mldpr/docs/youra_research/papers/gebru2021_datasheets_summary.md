# Paper Summary: Datasheets for Datasets
**Authors:** Gebru et al. | **Year:** 2021 | **arXiv:** 1803.09010

## Overview
Proposes "datasheets" — structured documentation cards for ML datasets analogous to
component datasheets in electronics. Defines a set of questions dataset creators should
answer covering: motivation, composition, collection process, preprocessing, uses,
distribution, and maintenance.

## Key Contributions
- Standardized documentation schema with 57 questions across 7 categories
- Demonstrates that most existing datasets lack adequate documentation
- "Intended Use" and "Out-of-Scope Use" fields directly encode misuse risk
- Widely adopted: HuggingFace dataset cards are structurally derived from datasheets

## Methodology
- Survey of dataset documentation practices across major ML datasets
- Expert panel to define documentation questions
- Case studies applying datasheet to existing datasets (Enron Email, ImageNet)

## Relevance to Gap 2
HuggingFace dataset cards inherit from this framework. Fields directly scorable:
- `intended_use` present → 1 point
- `out_of_scope_use` present → 1 point  
- `limitations` present → 1 point
- `task_categories` filled → 1 point
These scores can be computed programmatically via HuggingFace Hub API.
"Intended use" field enables task-type drift measurement: if a paper uses a dataset
outside its documented intended_use categories, that is an operationalized misuse signal.

## Limitations for Our Study
- HF card adoption is incomplete — many older datasets predate the standard
- Completeness score proxy for misuse risk requires empirical validation (our contribution)
- No existing ground truth linking card completeness to reproducibility outcomes
