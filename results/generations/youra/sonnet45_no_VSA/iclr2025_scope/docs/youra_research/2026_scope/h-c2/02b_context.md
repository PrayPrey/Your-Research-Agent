# Hypothesis Context: H-C2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-11
**Main Hypothesis:** H-APIContracts-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Cross-library contracts (multi-framework consistency) can detect integration defects before execution

### Type
CLAIM

### Rationale
Tests cross-framework integration defect detection capability. Modern ML pipelines increasingly require multi-framework interoperability (PyTorch → TensorFlow Lite, ONNX conversions, hybrid pipelines). Cross-framework integration introduces semantic inconsistencies (numerical discrepancies, operator incompatibilities, silent failures, dtype/shape mismatches) that manifest after deployment. Cross-library contracts validating multi-framework consistency can detect these defects before execution.

---

## Verification Protocol

### Conceptual Test
1. Implement cross-framework contracts (dtype preservation, shape consistency, numerical tolerance, operator semantics)
2. Test on real-world cross-framework conversion corpus (ONNX failures, CrossedWires models)
3. Measure detection rate vs end-to-end validation baseline
4. Validate execution time <5s for CI/CD integration
5. Assess false positive rate on valid conversions

### Success Criteria
- **Primary:** Detection rate ≥70% (outperforms end-to-end validation by ≥10pp)
- **Secondary:** Validation time <5s, false positive rate <10%, all 4 contract types detect ≥1 defect class

### Variables (if applicable)
- **Independent Variable:** Contract type (Dtype Preservation, Shape Consistency, Numerical Tolerance, Operator Semantics), Framework pair (PyTorch→TF, TF→PyTorch, PyTorch→JAX, *→ONNX)
- **Dependent Variable:** Detection rate, validation time, false positive rate
- **Controlled Variables:** Model architecture (VGG16, ResNet18, BERT-base), dataset (CIFAR-10, ImageNet subset, GLUE), conversion tool (ONNX, tf2onnx, torch2jax)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** ONNX Converter Failure Corpus + CrossedWires Models + Synthetic Defect Injection
- **Type:** Real-world corpus + controlled synthetic defects
- **Composition:**
  - ONNX Converter Failure Corpus (N=200): PyTorch/TensorFlow → ONNX conversion failures from arXiv:2303.17708
  - CrossedWires Models (N=2400 or stratified sample of 300): PyTorch/TensorFlow model pairs with accuracy discrepancies
  - Synthetic Defect Injection (N=500): Mutated valid conversions with known defect patterns
- **Rationale:** Real-world failures provide ecological validity; synthetic defects enable controlled evaluation; CrossedWires quantifies numerical tolerance issues
- **Accessibility:** ONNX failures from GitHub issues, CrossedWires dataset (340 GB or 30 GB sample), synthetic defects generated programmatically

### Selected Model/Baseline
- **Models:** VGG16, ResNet18/ResNet50, BERT-base, DenseNet121
- **Framework Pairs:** PyTorch→TensorFlow, TensorFlow→PyTorch, PyTorch→JAX, *→ONNX
- **Baselines:**
  1. No Validation (0% detection, ~0s)
  2. End-to-End Validation (40-60% detection, ~60s)
  3. Framework-Native Testing (20-30% detection, ~30s)
  4. ONNX Checker (30-40% detection, ~2s)
- **Rationale:** End-to-end validation is current best practice; must outperform by ≥10pp to demonstrate value

---

## Prerequisites

### Upstream Dependencies
- **H-M3 (VALIDATED):** Cross-library composition contracts detected 100% (6/6) cross-library defects within single frameworks at <1.5s execution time
- **Dependency:** H-C2 extends h-m3 from single-framework multi-library to multi-framework scenarios

### Validation Gate
- **Gate Type:** SHOULD_WORK (from prerequisites)
  - **PASS:** Detection rate ≥70%, validation time <5s, FPR <10%
  - **PARTIAL PASS:** Detection rate 50-70% (still useful, narrower scope)
  - **FAIL:** Detection rate <50% (not better than end-to-end validation)

---

## Literature Foundation

### Key References
1. **CrossedWires Dataset (2021)** [arXiv:2108.12768]: 0.681 accuracy difference on identical architectures across frameworks
2. **ONNX Converter Failures (2023)** [arXiv:2303.17708]: 75% of defects in operator conversion stage
3. **XAMT Cross-Framework API Matching (2024)** [arXiv:2508.12546]: 17 bugs detected across 839 matched APIs
4. **TensorScope Differential Testing (USENIX Security 2023)**: Cross-framework API inconsistencies in operator behavior
5. **DL Interoperability V&V (JAISCR 2023)** [doi:10.2478/jaiscr-2023-0016]: Multi-perspective validation approach

### Gap Analysis
- **Existing:** End-to-end validation (misses operator-level failures), differential testing (reactive, not preventive)
- **H-C2 Novelty:** Pre-execution validation at operator-level granularity with declarative contracts

---

## Phase 2C Connection

This context file serves as input to Phase 2C Experiment Design. The experiment brief (02c_experiment_brief.md) MUST:
1. Use the selected dataset (ONNX Corpus + CrossedWires + Synthetic)
2. Compare against the selected baselines (End-to-End, Framework-Native, ONNX Checker)
3. Target the success criteria (≥70% detection, <5s time, <10% FPR)
4. Build on prerequisite h-m3 validation results
5. Implement the 4 contract types specified in verification protocol

---

**Status:** COMPLETED (Phase 2B)
**Next Phase:** Phase 2C Experiment Design → Phase 3 Implementation Planning
