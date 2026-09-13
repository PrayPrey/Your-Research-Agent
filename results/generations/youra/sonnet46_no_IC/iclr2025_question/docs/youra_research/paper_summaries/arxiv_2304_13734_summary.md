# The Internal State of an LLM Knows When It's Lying

## Key Metadata
- **Authors:** Amos Azaria et al. (Ariel University; with Tom Mitchell, Carnegie Mellon University)
- **Year:** 2023
- **Venue:** Findings of EMNLP 2023 (arXiv 2304.13734); heavily cited (739+)
- **Core Contribution:** SAPLMA — a supervised feedforward classifier on LLM hidden-layer activations that predicts statement truthfulness (71–83% accuracy on held-out topics), demonstrating truthfulness is linearly extractable from internal states and that intermediate layers beat the final layer.

## Section Summaries

### Abstract
While Large Language Models (LLMs) have shown exceptional performance in various tasks, one of their most prominent drawbacks is generating inaccurate or false information with a confident tone. In this paper, we provide evidence that the LLM's internal state can be used to reveal the truthfulness of statements. This includes both statements provided to the LLM, and statements that the LLM itself generates. Our approach is to train a classifier that outputs the probability that a statement is truthful, based on the hidden layer activations of the LLM as it reads or generates the statement. Experiments demonstrate that given a set of test sentences, of which half are true and half false, our trained classifier achieves an average of 71% to 83% accuracy labeling which sentences are true versus false, depending on the LLM base model. We show that while LLM-assigned sentence probability is related to sentence truthfulness, this probability is also dependent on sentence length and the frequencies of words in the sentence, resulting in our trained classifier providing a more reliable approach.

### Introduction & Motivation
LLMs hallucinate with confident language. Hypothesis: to generate well, an LLM must internally represent whether a statement is true (e.g., after generating a false fact it tends to self-correct), so truthfulness should be extractable from hidden states. Three reasons models generate falsehoods anyway: (1) token-by-token commitment (the "Pluto is the smallest..." trap — locally likely tokens force globally false completions); (2) many correct completions dilute probability mass vs a single likely incorrect one; (3) sampling.

### Methodology
[DETAILED] **True-False dataset** (released): 6,084 statements over 6 disjoint topics — Cities (1,458), Inventions (876), Chemical Elements (930), Animals (1,008), Companies (1,200), Scientific Facts (612) — built by pairing entity properties from reliable tables (false = resampled property from another row) plus ChatGPT-generated/human-verified scientific facts. **SAPLMA:** feed each statement through the frozen LLM (OPT-6.7b, LLaMA2-7b; both 32 layers, d=4096), record hidden activations at candidate layers {last, 28th, 24th, 20th, middle(16th)} at the final token; train a feedforward classifier (3 hidden layers 256→128→64, ReLU, sigmoid output, Adam, 5 epochs, no hyperparameter tuning). **Key protocol:** leave-one-topic-out — train on 5 topics, test on the held-out topic (classifier must read the LLM's general "belief," not topic-specific patterns); 3 seeds averaged. Baselines: BERT-embedding classifier, 3-shot/5-shot prompting (probability ratio of "true"/"false" tokens), and "It-is-true-that-X" sentence-probability comparison.

### Experiments & Results
[DETAILED] **OPT-6.7b (Table 1):** SAPLMA average accuracy — last layer 0.6449, 28th 0.6507, 24th 0.6886, **20th layer 0.7098 (best)**, middle 0.6515. Baselines near chance: BERT 0.5434, 3-shot 0.5374, 5-shot 0.5370, It-is-true 0.5593. Per-topic: Cities up to 0.8125, Companies 0.8122 (well-represented topics), Elements/Animals ~0.60–0.62 (rarer topics). **LLaMA2-7b (Table 2):** stronger overall — average last 0.7107, 20th 0.8060, **middle(16th) layer 0.8298 (best)**; Cities 0.9223. NOTE: the optimal layer DIFFERS between models (OPT: 20/32; LLaMA2: 16/32). **LLM-generated statements** (245 OPT-generated, human-labeled, balanced): SAPLMA accuracy 0.62–0.64 (28th layer best, AUC 0.7614), baselines ≈ 0.50; with a validation-tuned threshold accuracy reaches 0.7134 (28th layer) — optimal layer also SHIFTS on this distribution (20th → 28th, statistically significant, p < 0.05). **Probability vs truth (Table 5):** raw sentence probability is confounded by length/word frequency/typos ("Kevin Duarnt is a basketball player": probability 1.5e-21 but SAPLMA correctly says true); SAPLMA output aligns with truth where probability fails. Random-label control: training accuracy drops 86.4% → 62.5%, showing the classifier exploits real structure.

### Discussion & Conclusion
LLMs possess an internal truthfulness representation distinct from sentence probability; SAPLMA can filter false statements before display. Limitations: English-only, per-statement activation capture (decoupling truth of the latest statement in long generations is open), threshold calibration needed for practical use.

## Key Contributions
- Evidence that truthfulness is encoded in hidden states and extractable with a simple supervised probe — with out-of-topic generalization.
- Intermediate layers (20th/32 for OPT, 16th/32 for LLaMA2) outperform the final layer for truthfulness reading — early evidence of the intermediate>final consensus AND of per-model optimal-layer variation.
- Released True-False dataset + demonstration that raw sentence probability is a confounded truthfulness signal (length/frequency).

## Potential Relevance
Foundational evidence for our Gap 1: hidden-state truthfulness signal EXISTS at intermediate layers, but extraction here is SUPERVISED (trained probe) — the training-free variant is exactly what's missing. Two findings directly support our design: (1) the optimal layer differs across models (OPT 20th vs LLaMA2 16th) and even across data distributions (20th vs 28th) — motivating per-model, held-out layer selection and warning about layer-transfer fragility (our detailed question 2); (2) raw sequence probability is confounded by surface statistics — analogous to our root-cause diagnosis of the h-e1 final-layer entropy failure (output-calibration confound), motivating pre-final-layer readouts. SAPLMA is also a natural supervised skyline/reference for the training-free signals we propose.
