# H-M2 Validation Report

**Generated:** 2026-03-15 13:06:35
**Hypothesis:** H-M2 — Bidirectional Semantic Accommodation Asymmetry
**Gate type:** SHOULD_WORK
**Gate result:** PASS

## Gate Evaluation

- Models passing (tiers_passing >= 2): 3/3
- Passing models: ['minilm', 'paraphrase', 'mpnet']
- Gate threshold: models_passing >= 2

## Model Results

### Model: minilm
- tiers_passing: 3
- gate_passed: True

  **helpful-base**
  - C_sem^H←A = 0.0853
  - C_sem^A←H = 0.0395
  - p_value = 0.0
  - cohen_d = 0.3734540045261383

  **helpful-rejection-sampled**
  - C_sem^H←A = 0.0923
  - C_sem^A←H = 0.0535
  - p_value = 0.0
  - cohen_d = 0.3303290903568268

  **helpful-online**
  - C_sem^H←A = 0.0876
  - C_sem^A←H = 0.0718
  - p_value = 4.832617987271606e-30
  - cohen_d = 0.1332729607820511

### Model: paraphrase
- tiers_passing: 3
- gate_passed: True

  **helpful-base**
  - C_sem^H←A = 0.0794
  - C_sem^A←H = 0.0316
  - p_value = 0.0
  - cohen_d = 0.40526920557022095

  **helpful-rejection-sampled**
  - C_sem^H←A = 0.0866
  - C_sem^A←H = 0.0433
  - p_value = 0.0
  - cohen_d = 0.385294109582901

  **helpful-online**
  - C_sem^H←A = 0.0847
  - C_sem^A←H = 0.0617
  - p_value = 4.508341485277738e-81
  - cohen_d = 0.20488037168979645

### Model: mpnet
- tiers_passing: 3
- gate_passed: True

  **helpful-base**
  - C_sem^H←A = 0.0826
  - C_sem^A←H = 0.0422
  - p_value = 0.0
  - cohen_d = 0.33376944065093994

  **helpful-rejection-sampled**
  - C_sem^H←A = 0.0884
  - C_sem^A←H = 0.0581
  - p_value = 0.0
  - cohen_d = 0.261107474565506

  **helpful-online**
  - C_sem^H←A = 0.0838
  - C_sem^A←H = 0.0767
  - p_value = 0.004117539922906984
  - cohen_d = 0.06063465774059296

## Consistency Check

- consistent_count: 3
- gate_passed: True

## Mechanism Activation

- Mechanism activated: True
  - both_directions_computed: True
  - shapes_match: True
  - asymmetry_nonzero: True
  - fr_m2_logs_found: True

## Interpretation

Gate PASS: H-M2 confirmed. Human-to-AI accommodation (H←A) is significantly stronger than AI-to-Human accommodation (A←H) across >= 2/3 models and >= 2 tiers.
