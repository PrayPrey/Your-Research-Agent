---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Weight Space Learning Without Complex Equivariance"
---

# Research Brainstorm Session Results

**Session Date:** 2026-07-11
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Exploring neural network weights as a new data modality, focusing on practical approaches to weight space learning that avoid high-complexity equivariant architectures and framework incompatibilities.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode) - Learning from 5 previous hypothesis failures to generate a feasible research direction.

**Session Duration:** < 1 minute (automated extraction with failure context integration)

---

## Starting Context

The ICLR 2025 Workshop on Neural Network Weights as a New Data Modality addresses a critical gap in deep learning research. With over a million publicly available neural network models on platforms like Hugging Face, weight space learning has emerged as a nascent but scattered research area.

**Research Direction (NEW - informed by failure analysis):** This attempt focuses on **practical weight space learning approaches** that can be implemented with standard PyTorch infrastructure, avoiding:
- JAX/PyTorch cross-framework dependencies
- Re-implementation of complex equivariant architectures (GNNs, NFN)
- Large-scale dataset downloads (2.6TB model zoos)
- High-complexity implementation tasks (50+ hour estimates)

---

## Lessons from Previous Attempts

### Summary of Previous Failures

**Previous Direction:** "Weight space embeddings that capture meaningful model relationships and enable prediction of model capabilities"

**5 Hypothesis Failures Analyzed:**

1. **h-e1 Run 1 (IMPLEMENTATION_INCOMPLETE)**: Attempted to implement SANE Transformer encoder from scratch. Failed due to:
   - 103 complexity score, 50+ hour estimate
   - 2.6TB ModelZooDataset requiring custom download infrastructure
   - Exceeded batch execution capacity

2. **h-e1 Run 2 (INFRASTRUCTURE_INCOMPATIBILITY)**: Attempted Universal Neural Functional (UNF) with simplified PyTorch encoder. Failed due to:
   - JAX/PyTorch framework incompatibility
   - Equivariance error 10^-1 vs 10^-6 threshold (5 orders of magnitude gap)
   - Simplified DeepSets encoder insufficient for precision requirements

3. **h-e1 Run 3 (MUST_WORK_GATE_FAILED)**: Attempted heuristic architecture detection. Failed due to:
   - MAE 0.2942 vs random baseline 0.1208 (143.5% worse)
   - Dataset acquisition only 9/20 models (PyTorch/transformers version conflicts)
   - Soft vs hard label mismatch in evaluation
   - Single architecture family (Hybrid only) in validation set

4. **h-e2 Run 1 (FUNDAMENTAL_API_MISMATCH)**: Attempted NFN library for permutation extraction. Failed due to:
   - NFN designed for weight-space meta-learning (batch of networks), not single-model analysis
   - API expects shape [BatchSize, Channels, ...], ResNet has [C_out, C_in, H, W]
   - Manual permutation fallback also failed (0/10 functional equivalence tests)

5. **h-m2 Run 1 (MUST_WORK_GATE_FAILED)**: Attempted NFN vs MLP scaling comparison. Failed due to:
   - Simplified residual connections instead of true NPLayers
   - Training loss mismatch 23-8643% (target <1%)
   - NFN test error 0.0550 vs MLP 0.0001 (NFN 54900% worse)

### Critical Lessons for THIS Attempt

**What to AVOID:**
1. ❌ **Complex equivariant architectures requiring re-implementation** (SANE, UNF, NFN)
2. ❌ **JAX libraries when infrastructure is PyTorch-based** (cross-framework conversion loses precision)
3. ❌ **Large-scale dataset downloads** (2.6TB ModelZooDataset, 50GB truncated versions)
4. ❌ **Libraries designed for different use cases** (NFN is for meta-learning, not checkpoint analysis)
5. ❌ **Simplified approximations of complex methods** (residual connections ≠ permutation-equivariant layers)
6. ❌ **High-complexity hypotheses in batch mode** (complexity > 80, time > 8 hours)
7. ❌ **Tight numerical precision requirements** (10^-6 thresholds unachievable with simplified encoders)

**What WORKS (Evidence from Partial Success):**
1. ✅ **Standard PyTorch infrastructure** (torchvision, TIMM library for model access)
2. ✅ **Small-scale validation datasets** (10-20 models, not full model zoos)
3. ✅ **Heuristic pattern detection** (4D conv detection, Q/K/V matrix patterns worked correctly)
4. ✅ **Pre-trained model loading from standard sources** (TIMM provides reliable access)
5. ✅ **Fast iteration cycles** (<1 hour execution, vs 50+ hour implementation)
6. ✅ **Relaxed numerical thresholds** (10^-2 achievable, vs 10^-6 unrealistic)

### How THIS Direction Avoids Those Pitfalls

**New Approach - "Practical Weight Statistics for Architecture Inference":**

1. **Use Weight Statistics Instead of Equivariant Encoders:**
   - Replace SANE/UNF/NFN with simple statistical features (tensor shapes, norms, distribution moments)
   - No permutation equivariance requirements (avoid precision/complexity issues)
   - Standard PyTorch tensor operations only

2. **Focus on Architecture Family Classification (Not Performance Prediction):**
   - Predict architecture family (CNN/Transformer/Hybrid) from weight patterns
   - Use balanced validation sets (not single architecture family)
   - Hard label classification (avoid soft label mismatches)

3. **Use TIMM Library Exclusively (No HuggingFace/Transformers Conflicts):**
   - Avoid version conflicts that blocked 55% of downloads in h-e1 Run 3
   - Reliable model access without dependency issues
   - 1000+ vision models available

4. **Small-Scale Validation (10-50 Models, Not 2.6TB):**
   - Download only necessary checkpoints from TIMM
   - No custom dataset infrastructure required
   - Fits in batch execution time budget (<8 hours)

5. **Achievable Complexity Budget:**
   - Estimated 3-5 implementation tasks, complexity score <30
   - No architecture re-implementation (just statistical feature extraction)
   - Pre-trained models from TIMM (no training required)

---

## Session Plan

**Objective:** Design feasible weight space learning experiments that can be executed in PyTorch batch mode without high-complexity dependencies.

**Approach:**
1. Statistical analysis of weight tensors (shapes, norms, sparsity, distribution moments)
2. Heuristic pattern detection validated in previous runs (4D conv, attention matrices)
3. Classification task with balanced dataset and consistent evaluation
4. Standard PyTorch infrastructure with TIMM library
5. Complexity budget <40, execution time <8 hours

---

## Technique Sessions

### Weight Statistical Feature Extraction
- Tensor shape patterns (4D for conv, 2D for linear, 3D for attention)
- Weight norm distributions (layer-wise L1/L2 norms)
- Sparsity patterns (percentage of near-zero weights)
- Distribution moments (mean, std, skewness, kurtosis per layer)
- Activation function heuristics (ReLU→positive bias, GELU→different distribution)

### Architecture Pattern Detection (Validated from h-e1 Run 3)
- CNN detection: 4D convolution tensor shape [C_out, C_in, H, W]
- Transformer detection: Q/K/V attention matrix patterns [D_model, D_model]
- Hybrid detection: Presence of both conv and attention layers
- Normalization layer patterns (BatchNorm vs LayerNorm statistics)

### Balanced Dataset Construction (Addressing h-e1 Run 3 Failure)
- Equal representation across architecture families (CNN, Transformer, Hybrid)
- TIMM library provides diverse model collection
- Validation: Ensure each family has ≥3 models in test set
- No dependency conflicts (TIMM only, avoid HuggingFace/transformers)

---

## Research Question Development

### Initial Question

Can simple statistical features extracted from neural network weight tensors reliably classify model architecture families (CNN/Transformer/Hybrid) without requiring forward passes or complex equivariant encoders?

### Refined Question

Can we achieve >80% accuracy in classifying pre-trained vision models into architecture families (CNN/Transformer/Hybrid) using only weight tensor statistics (shapes, norms, sparsity, distribution moments) extracted via standard PyTorch operations, validated on TIMM model zoo?

### Detailed Sub-Questions

1. **Weight Shape Patterns**: Do 4D tensor presence (conv layers) vs 2D tensor patterns (linear layers) with specific dimension ratios reliably separate CNN vs Transformer architectures?

2. **Normalization Layer Fingerprints**: Can BatchNorm vs LayerNorm parameter statistics distinguish CNNs from Transformers (BatchNorm common in CNNs, LayerNorm in Transformers)?

3. **Weight Distribution Characteristics**: Do weight norm distributions differ significantly between architecture families due to different initialization schemes and training dynamics?

4. **Hybrid Architecture Detection**: Can we detect hybrid models (ConvNeXt, RegNet) by identifying both conv and attention layer patterns in the same checkpoint?

5. **Generalization Across Model Families**: Does the classifier trained on ResNet/ViT/ConvNeXt generalize to unseen families (EfficientNet, DeiT, Swin Transformer)?

---

## Reference Papers

### Weight Space Analysis (No Complex Equivariance)
- Weight statistics for model characterization
- Neural network fingerprinting via weight signatures
- Model family identification from checkpoints
- Architecture inference without forward passes

### Practical Model Zoo Analysis
- TIMM library model collections
- Model metadata extraction
- Architecture classification benchmarks
- Transfer learning relationship discovery

### Statistical Pattern Detection
- Tensor shape analysis for architecture detection
- Weight norm distributions across model families
- Sparsity patterns in different architectures
- Normalization layer statistical fingerprints

**Note:** Phase 1 will gather specific papers using semantic scholar, focusing on practical weight analysis methods that don't require equivariant architectures.

---

## Validation Results

### So What Test

**Impact Statement:** If successful, this research would enable:

1. **Rapid Architecture Identification:** Practitioners could quickly determine model architecture families from checkpoints without requiring architecture specifications or forward passes, useful for model auditing and verification.

2. **Practical Weight Space Baselines:** Establish simple statistical baselines for weight space learning that don't require complex equivariant architectures, providing accessible entry points for the field.

3. **Model Zoo Organization:** Enable automatic categorization of large model collections based on weight patterns, improving model discovery and organization on platforms like Hugging Face.

4. **Foundation for Complex Methods:** Statistical features validated here can serve as input to more sophisticated weight space learning methods, bridging simple heuristics and complex equivariant approaches.

**Why It Matters:** Current weight space learning research focuses on complex equivariant methods (SANE, UNF, NFN) that are difficult to implement and validate. Simple statistical approaches provide practical alternatives that work with standard infrastructure.

### Feasibility Check

**✅ PASSES ALL MANDATORY CONSTRAINTS:**

1. **No New Benchmarks Required:** Uses TIMM model zoo (1000+ pre-trained models) with existing architecture family labels (CNN/Transformer/Hybrid).

2. **No Synthetic/Generated Data:** Operates on real pre-trained model weights from TIMM library. No model training required.

3. **No Human Evaluation:** Validation uses objective metrics:
   - Architecture family classification accuracy (predicted label vs ground truth)
   - Precision/recall per family (balanced evaluation)
   - Confusion matrix analysis (systematic error patterns)

4. **Immediate Testing Possible:**
   - Download 10-50 models from TIMM (< 5GB total)
   - Extract statistical features via PyTorch tensor operations
   - Train simple classifier (Logistic Regression or shallow MLP)
   - Validate on balanced test set

**✅ ADDRESSES PREVIOUS FAILURE ROOT CAUSES:**

1. **Low Complexity:** Statistical feature extraction requires 3-5 tasks, complexity <30 (vs 103 for SANE re-implementation)
2. **No Framework Conflicts:** Pure PyTorch, no JAX dependencies (vs UNF incompatibility)
3. **Small Dataset:** 10-50 models from TIMM, <5GB (vs 2.6TB ModelZooDataset)
4. **No API Mismatches:** Direct PyTorch state_dict access, no library assumptions (vs NFN API mismatch)
5. **Achievable Baselines:** Statistical classification has established baselines (vs novel equivariant methods)
6. **Fast Execution:** <2 hours for full experiment (vs 50+ hours for SANE implementation)

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can we achieve >80% accuracy in classifying pre-trained vision models into architecture families using only weight tensor statistics extracted via standard PyTorch operations?

### detailed_question
1. Do 4D tensor presence vs 2D tensor patterns reliably separate CNN vs Transformer architectures?
2. Can BatchNorm vs LayerNorm parameter statistics distinguish architecture families?
3. Do weight norm distributions differ significantly between CNNs, Transformers, and Hybrids?
4. Can we detect hybrid models by identifying both conv and attention patterns?
5. Does the classifier generalize across unseen model families?

### reference_papers
Weight statistics for model characterization, neural network fingerprinting, model family identification, architecture inference without forward passes, TIMM model zoo analysis, tensor shape analysis for architecture detection, weight norm distributions, normalization layer statistical fingerprints, practical weight space learning baselines

</phase1-input>

---

## Session Insights

### Key Discoveries

1. **Failure Analysis Drives Scope Reduction:** 5 hypothesis failures converged on a common theme - complex equivariant methods (SANE, UNF, NFN) are too difficult to implement correctly in batch mode. Statistical approaches bypass this complexity.

2. **Infrastructure Constraints Are Hard Constraints:** JAX/PyTorch incompatibility is not a minor issue - it breaks numerical precision guarantees and makes validation impossible. Staying within PyTorch ecosystem is mandatory.

3. **Dataset Scale Mismatch:** 2.6TB model zoos are incompatible with batch execution time budgets. Small-scale validation (10-50 models) is sufficient for proof-of-concept and avoids download infrastructure complexity.

4. **Heuristic Validation Shows Promise:** Despite h-e1 Run 3 failure, the core heuristics (4D conv detection, attention matrix patterns) worked correctly. The failure was due to evaluation setup (label mismatch, single architecture family), not the detection method.

5. **Complexity Budget Enforcement:** The pipeline's complexity threshold (score <40, time <8 hours) should be treated as a HARD constraint, not a guideline. Hypotheses exceeding this budget should be rejected in Phase 3, not allowed to fail in Phase 4.

### Techniques Used

- **Failure Root Cause Synthesis:** Analyzed 5 failure memories to extract common failure modes
- **Constraint-Driven Redesign:** Applied feasibility constraints to eliminate approaches that failed before
- **Partial Success Preservation:** Retained validated components (TIMM library, heuristic detection) while removing failures (equivariant architectures, large datasets)
- **Complexity Budget Validation:** Designed approach to fit within proven execution capacity

### Areas for Further Exploration

1. **Feature Engineering:** Which statistical features are most discriminative for architecture family classification?
2. **Model Selection:** Which TIMM models provide best diversity for training and testing?
3. **Baseline Methods:** What accuracy can be achieved with random guessing, majority class, or metadata-based classification?
4. **Scalability:** How does classification accuracy scale with training set size (10 vs 50 vs 100 models)?
5. **Transferability:** Can features learned on vision models transfer to NLP or multimodal architectures?

---

## Next Steps

**Phase 1: Targeted Research**
- Use semantic scholar to find: weight statistics for model analysis, architecture fingerprinting methods, model zoo classification papers
- Use Archon KB to search: statistical feature extraction for neural networks, checkpoint analysis techniques, architecture detection heuristics
- Use Exa search to find: TIMM model zoo documentation, PyTorch state_dict tutorials, model metadata extraction code

**Archon Pipeline Setup:**
- Create "Anonymous Pipeline: Weight Space Learning Without Complex Equivariance" project
- Initialize 9 phase tasks (skip Phase 5 as per module config: skip_baseline_comparison=true)
- Mark Phase 0 → done, Phase 1 → doing

**Focus Areas for Phase 1:**
1. Survey simple weight analysis techniques (no equivariance required)
2. Identify discriminative statistical features for architecture families
3. Find TIMM model subset with balanced architecture family distribution
4. Establish baseline accuracy for metadata-based classification
5. Assess computational requirements (<8 hours execution time)

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
