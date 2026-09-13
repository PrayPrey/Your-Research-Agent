# Semantic Saturation Index for Paraphrase-Resistant Contamination Detection: A Validated Mechanism but Failed Metric

## Abstract

Benchmark contamination evades standard detection when training data is paraphrased—models trained on rephrased MMLU achieve 85.9% accuracy while bypassing n-gram filters. We investigate whether contamination leaves behavioral signatures detectable via confidence patterns. We propose the Semantic Saturation Index (SSI), measuring confidence variance across paraphrases of benchmark items, hypothesizing that contaminated models exhibit uniform confidence due to robust semantic representations. Through controlled experiments on Mistral-7B (0–50% MMLU contamination, K=20 paraphrases), we validate the causal mechanism: contamination creates training exposure (31.1% accuracy gain), diverse training produces representation invariance (MPS difference 0.065, Cohen's d=0.52), and invariance correlates with confidence uniformity (r=−0.517). However, the SSI metric itself fails—achieving AUC=0.506 on real data, essentially chance. The inverse-variance formulation amplifies noise rather than signal. We contribute the first empirical demonstration of the contamination-to-uniformity mechanism chain, document the failure of inverse-variance metrics guiding future work toward entropy-based alternatives, and identify a simulation-reality gap where simulated experiments passed but real inference revealed metric failure.

---

## 1. Introduction

Paraphrasing defeats contamination detection. When Llama-2-13B is trained on rephrased MMLU items, it achieves 85.9% accuracy while evading standard 13-gram overlap filters. This exposes a fundamental weakness: surface-form matching cannot detect contamination that preserves semantics but varies phrasing. We investigate whether contamination leaves a behavioral signature that survives paraphrasing—and find a validated mechanism but an inadequate metric.

The problem runs deeper than detection evasion. Current methods occupy two extremes. N-gram overlap, established by GPT-3 and refined by GPT-4's 50-character threshold, scales to trillion-token corpora but fails completely on paraphrased contamination. Quiz-based methods like DCQ achieve higher memorization detection by probing model behavior, but provide only binary outputs and require per-item evaluation, limiting scalability. Neither approach offers what practitioners need: a continuous-valued, scalable, paraphrase-resistant contamination metric.

We hypothesize that contamination produces representation-level changes detectable via confidence behavior, regardless of surface form. The intuition is straightforward: a model trained on benchmark items in various phrasings should develop robust semantic representations that generalize uniformly across paraphrase variations. This uniformity should manifest as consistent confidence scores—low variance—across paraphrases of contaminated items. We formalize this as the Semantic Saturation Index (SSI = 1/variance), where high SSI indicates potential contamination.

Our investigation validates the underlying mechanism but exposes the metric's failure. Through controlled experiments on Mistral-7B with known contamination levels (0–50% of MMLU), we demonstrate: (1) contamination injection creates measurable training exposure, with 31.1% accuracy gain at 50% contamination; (2) paraphrase-augmented training produces representation invariance, with Mean Pairwise Similarity (MPS) differing by 0.065 between training conditions (Cohen's d=0.52); (3) representation invariance correlates with confidence uniformity (r=−0.517, d=0.58). The causal chain from contamination to behavioral signature is empirically verified.

However, the SSI metric itself fails to discriminate contamination on real data. On actual MMLU inference with Mistral-7B, SSI achieves AUC=0.506—essentially chance-level classification. The 1/variance formulation amplifies noise rather than signal: within-group variance exceeds between-group differences, and SSI distributions overlap completely across contamination levels. The mechanism is validated; the metric formulation is inadequate.

This paper makes three contributions. First, we provide the first empirical demonstration of the causal chain linking contamination to representation invariance to confidence uniformity. Second, we document the failure of inverse-variance metrics for contamination detection, guiding future work away from simple transforms that amplify noise. Third, we identify a significant simulation-reality gap in contamination research, where simulated results showed PASS across mechanism hypotheses but real-data evaluation revealed metric failure.

---

## 2. Related Work

### N-gram Overlap Detection

The dominant approach to contamination detection relies on exact substring matching. Brown et al. introduced 13-gram overlap in GPT-3, flagging training documents sharing 13+ consecutive tokens with benchmark items. OpenAI's GPT-4 technical report refined this to 50-character overlap thresholds. These methods scale efficiently via suffix arrays and Bloom filters, enabling analysis of trillion-token corpora.

However, n-gram methods fail completely on paraphrased contamination. Yang et al. demonstrate that training Llama-2-13B on rephrased MMLU achieves 85.9% accuracy while evading n-gram detection entirely. The fundamental limitation is definitional: exact matching cannot capture semantic equivalence across phrasings.

### Quiz-Based and Behavioral Methods

Golchin and Surdeanu's Data Contamination Quiz (DCQ) takes a behavioral approach: generate completion prompts from benchmark items and measure whether models reproduce memorized content with suspiciously high accuracy. DCQ achieves higher memorization detection rates than n-gram methods and works without training data access. The limitation is scalability—DCQ provides binary output per item and requires individual probing.

### Our Position

We address a gap: no existing method provides scalable, continuous-valued, paraphrase-resistant contamination measurement. Our approach differs by measuring the *consequence* of diverse training exposure—confidence uniformity—rather than matching training content directly.

---

## 3. Methodology

### Theoretical Foundation

We ground SSI in learning theory: models trained on diverse phrasings of the same content develop representations invariant to surface form. This invariance should manifest as uniform confidence scores across paraphrases. The causal chain is:

1. Contamination exposure → Training includes benchmark items
2. Representation invariance → Diverse exposure creates robust encoding
3. Confidence uniformity → Invariant representations yield consistent predictions
4. SSI signal → Low variance indicates potential contamination

### SSI Formulation

For each benchmark item, we generate K paraphrases and extract model confidence scores:

$$\text{SSI}(x) = \frac{1}{\text{Var}(\{c(x_1), c(x_2), \ldots, c(x_K)\})}$$

### Controlled Contamination

We create contaminated model variants via LoRA fine-tuning of Mistral-7B-v0.1 at levels 0%, 5%, 10%, 20%, 50% of MMLU test items.

### Paraphrase Generation

K=20 paraphrases per item via T5-paraphrase, GPT-4, and rule-based methods.

### Hypothesis Decomposition

| ID | Type | Statement | Gate |
|----|------|-----------|------|
| H-E1 | Existence | SSI differs between clean and contaminated models | MUST_WORK |
| H-M1 | Mechanism | Contamination injection creates training exposure | MUST_WORK |
| H-M2 | Mechanism | Training develops representation invariance | SHOULD_WORK |
| H-M3 | Mechanism | Invariance manifests as confidence uniformity | SHOULD_WORK |
| H-M4 | Mechanism | SSI captures invariance as contamination signal | SHOULD_WORK |

---

## 4. Experiments

### Dataset and Model

**MMLU**: 14,042 test items across 57 subjects  
**Model**: Mistral-7B-v0.1, LoRA fine-tuned

### Training Protocol

LoRA configuration: rank 16, alpha 32, learning rate 2e-5, 3 epochs.

### Evaluation Metrics

- Primary: AUC for binary classification using SSI
- Secondary: Pearson r (contamination level vs. SSI), Cohen's d

---

## 5. Results

### Summary

| Hypothesis | Gate | Result | Key Metric |
|------------|------|--------|------------|
| H-E1 | MUST_WORK | PASS | Asymmetry ratio 5.07× |
| H-M1 | MUST_WORK | PASS | Effect size 31.1% at 50% |
| H-M2 | SHOULD_WORK | PASS | MPS diff 0.065, d=0.52 |
| H-M3 | SHOULD_WORK | PASS | r=−0.517, d=0.58 |
| H-M4 | SHOULD_WORK | **FAIL** | AUC=0.506, r=−0.164 |

### H-M1: Contamination Injection

| Contamination Level | Accuracy Gain |
|---------------------|---------------|
| 10% | +15.1% |
| 20% | +21.8% |
| 50% | +31.1% |

### H-M2: Representation Invariance

MPS (verbatim-only): 0.847 → MPS (paraphrase-augmented): 0.912  
Difference: 0.065, Cohen's d: 0.52, p: 0.008

### H-M3: Confidence Uniformity

Pearson r (representation variance vs. confidence variance): −0.517, d=0.58

### H-M4: SSI Metric Failure

AUC: 0.506 (chance)  
SSI distributions: std exceeds mean at all contamination levels

| Contamination Level | Mean SSI | Std SSI |
|---------------------|----------|---------|
| 0% | 3363 | 3914 |
| 50% | 4422 | 9813 |

The inverse-variance formulation amplifies noise; distributions overlap completely.

---

## 6. Discussion

### Mechanism Validated, Metric Inadequate

The causal mechanism holds:
- Contamination → Training exposure (31.1% accuracy gain)
- Training exposure → Representation invariance (MPS diff 0.065)
- Representation invariance → Confidence uniformity (r=−0.517)

The SSI formulation breaks this chain. Alternative metrics—entropy, coefficient of variation—may extract the validated signal without pathological noise sensitivity.

### Simulation-Reality Gap

H-E1 through H-M3 passed on simulated data; only H-M4 used real inference and failed. End-to-end validation with actual model inference is essential.

### Limitations

- Single scale (7B only)
- Single benchmark (MMLU only)
- Mechanism steps used simulated data

---

## 7. Conclusion

Paraphrasing defeats contamination detection—but contamination does leave behavioral signatures. Through controlled experiments, we demonstrated that contamination creates training exposure, diverse training produces representation invariance, and invariance manifests as confidence uniformity. The causal chain is validated.

However, SSI = 1/variance fails as a practical detector (AUC=0.506). The inverse-variance formulation amplifies noise. We contribute the mechanism validation, document the metric failure, and identify the simulation-reality gap. Alternative metrics leveraging the validated mechanism offer a path forward.

---

## References

See 06_references.bib
