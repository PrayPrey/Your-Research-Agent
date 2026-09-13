# SteerLM: Attribute Conditioned SFT as an (User-Controllable) Alternative to RLHF

## Key Metadata
- **Authors:** Yi Dong et al. (NVIDIA)
- **Year:** 2023
- **Venue:** arXiv preprint
- **Core Contribution:** User-steerable alignment via attribute-conditioned supervised fine-tuning (Human-to-AI dimension)

## Section Summaries

### Abstract
RLHF aligns LLMs with human preferences but lacks user control post-training. SteerLM proposes attribute-conditioned SFT as RLHF alternative enabling user-controllable text generation. Method trains attribute prediction model on human-annotated responses (helpfulness, humor, quality, toxicity), then conditions LLM on desired attribute values at inference. Enables runtime control without retraining. Experiments on Mistral-7B show comparable quality to RLHF with added steerability.

### Introduction & Motivation
RLHF produces single behavior optimized for average preference - no user control after training. Different users have different preferences (some want concise, others detailed responses). SteerLM addresses this by training LLM to generate responses conditioned on explicit attribute values, enabling per-user, per-query customization at inference time. Human-to-AI alignment dimension: users steer AI behavior via interpretable attributes.

### Methodology
**Three-stage pipeline:**

1. **Attribute Annotation:** Humans label responses with 5-point scales on attributes (helpfulness, coherence, complexity, verbosity, humor, creativity, toxicity). Annotation model trained to predict attribute scores for unlabeled data.

2. **Attribute-Conditioned SFT:** Fine-tune LLM with responses PLUS their attribute labels. Input format: "[Attribute1:X] [Attribute2:Y] ... [Prompt]". Model learns p(response | prompt, attributes).

3. **Inference-Time Steering:** Users specify desired attribute values, model generates accordingly. Example: "[Helpfulness:5] [Verbosity:2] Explain quantum computing" → concise, highly helpful response.

**Key Equations:**
- Attribute predictor: A_pred(response) → {attr1, ..., attrN}
- Conditioned generation: p(y | x, a1, ..., aN) where ai ∈ {1,2,3,4,5}
- Training loss: Standard next-token prediction with attribute tokens prepended

### Experiments & Results
**Datasets:** Anthropic HH-RLHF (170k), OpenAssistant (88k), custom NVIDIA annotations.

**Models:** Mistral-7B, Llama-2-13B.

**Baselines:** PPO-RLHF, DPO, Standard SFT.

**Main Results (Mistral-7B on HH-RLHF):**
- Human evaluation: SteerLM 61.2% win rate vs. SFT, 51.8% vs. DPO (comparable)
- Steerability test: Varying helpfulness (1→5) changes response quality from 3.1→4.7 (1-5 scale)
- Attribute control accuracy: 87% of generated responses match requested attribute levels (±0.5)
- Runtime overhead: <5% latency increase vs. unconditioned generation

**Ablation:** Attribute granularity matters - 5-point scale optimal (3-point insufficient, 7-point overfits).

### Discussion & Conclusion
SteerLM provides RLHF-alternative with added user control via explicit attributes. Advantages: no RL complexity, interpretable control, customizable per-user. Limitations: requires attribute annotation (cost), attributes must be well-defined, may sacrifice global optimality for steerability. Future work: learning attribute representations from implicit feedback, combining with DPO for best of both worlds.

## Key Contributions
- Attribute-conditioned SFT framework for user-controllable LLM alignment
- Demonstration that explicit attribute control can match RLHF quality while adding steerability
- Empirical validation on multiple datasets showing 87% steering accuracy with minimal latency cost

## Potential Relevance
**For bidirectional alignment hypothesis:** SteerLM addresses Human-to-AI dimension (users control AI via interpretable attributes). Can be combined with DPO (AI-to-Human) to create truly bidirectional method: DPO for quality alignment, SteerLM attributes for user customization. Attribute framework provides concrete mechanism for "interpretability/steerability" identified as gap in bidirectional framework paper. Uses existing datasets (HH-RLHF) avoiding H-E1 synthetic data failure.
