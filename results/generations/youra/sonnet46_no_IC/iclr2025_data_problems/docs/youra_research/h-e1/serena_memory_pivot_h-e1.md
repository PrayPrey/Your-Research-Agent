# Pivot Record: h-e1 → h-e1-v2

**Date:** 2026-08-04T16:50:00Z  
**Hypothesis:** h-e1 (Scale-Dependent Optimal Curation — Existence Test)  
**Pivot Type:** SCOPE_REDUCTION  
**Gate:** MUST_WORK PARTIAL  
**New Hypothesis:** h-e1-v2

## Why Pivoted

PoC proxy models (7M/16M params, 200 steps) cannot exhibit scale-dependent curation effects. Pipeline mechanism verified; statistical signal requires real model scales.

## What Changed

- Model scales: 70M/160M → 14M/31M
- Token budget: 50B → 1B
- Corpus: Dolma+FineWeb → FineWeb only

## Code Reuse

All code in `h-e1/code/` is reusable unchanged. Only `config.py` scale configs need updating.

## Lessons

- PoC needs ≥14M/31M (2.2× ratio) with ≥1B tokens for benchmark signal
- MMLU floors at 0.05 for <200-step models; use HellaSwag as primary metric
- GPT-2 PPL filter essential; char-entropy proxy insufficient
