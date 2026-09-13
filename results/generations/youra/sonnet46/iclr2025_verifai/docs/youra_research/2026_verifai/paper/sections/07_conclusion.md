# 7. Conclusion

We began by asking whether you should trust LLM confidence when it fails at code. The answer, we found, depends on the model's architecture.

Our study provides the first difficulty-stratified calibration fingerprint for LLM code verifiers using P(True) logprob confidence. By generating k=5 solutions per problem and stratifying by each model's own pass@1 distribution, we designed a self-contained methodology that reveals each model's calibration fingerprint without relying on external difficulty labels. Testing three architectures at 7–8B scale — code-specialized (DeepSeek-Coder), code-adapted (CodeLlama), and general-purpose (Llama3) — we found that ΔECE direction is architecture-determined: +0.298 (code-specialized, expected), −0.249 (code-adapted, inverted), and ≈0 (general-purpose, insensitive). The original hypothesis that ΔECE > 0 in ≥2/3 model families is refuted; the architecture-stratified finding is richer and more informative.

Our contributions are:

1. **A validated self-contained calibration pipeline**: k=5 solution generation → tier stratification → P(True) extraction → M=15-bin ECE with bootstrap CI, achieving perfect coverage across all model-benchmark combinations and non-degenerate confidence distributions (std 0.062–0.078). This infrastructure is reusable for future difficulty-stratified calibration studies on EvalPlus.

2. **An architecture-dependent ΔECE fingerprint**: The sign of ΔECE differentiates code-specialized, code-adapted, and general-purpose architectures at 7–8B scale. This finding argues against universal confidence threshold policies in code verification pipelines — practitioners must characterize their specific model's calibration fingerprint.

3. **Evidence for training data composition as the mechanism**: CodeLlama's extreme T*=3.95 and inverted ΔECE (−0.249) suggest that code fine-tuning on common utility patterns creates systematic overconfidence on MBPP-style easy problems. Global temperature scaling cannot correct this architecture-specific pathology.

4. **An architecture-independent difficulty iron core**: 133/542 (24.5%) EvalPlus problems are universally hard regardless of architecture (Jaccard 0.456–0.546), providing a robust calibration benchmark for future multi-model comparison studies.

## Future Directions

**From untested alternative explanations.** The training data composition hypothesis for CodeLlama's inversion should be tested directly: compare P(True) values on easy-tier MBPP problems that appear in CodeLlama's training corpus versus those that do not. If seen problems receive systematically higher P(True) regardless of EvalPlus correctness, the overconfidence-on-pattern hypothesis is confirmed.

**From scope extension.** Replicating with k≥20 solutions would provide finer difficulty stratification (continuous rather than 6-point pass@1) and a larger CodeLlama easy tier (n=37 is near-minimum for M=15 ECE bins). Tier-specific temperature scaling (fitting separate T_hard and T_easy) may prove a more effective post-hoc correction than global T for architecture-dependent ΔECE. Testing instruction-tuned variants (Llama3-8B-Instruct, CodeLlama-Instruct, DeepSeek-Coder-Instruct) would clarify whether RLHF/SFT training preserves or alters the architecture-dependent calibration fingerprint.

**From unverified assumptions.** Expanding to N≥2 models per architecture category would allow within-category replication: does ΔECE direction generalize to Mistral-7B (second general-purpose model) or WizardCoder-7B (second code-adapted model)? A confirmatory study with broader model coverage would establish whether architecture categories reliably predict ΔECE direction or whether the pattern is idiosyncratic to our three specific models.

Understanding calibration is not just about asking whether a model is well-calibrated — it requires asking what the model was trained to be confident about. For code verification at scale, the architecture behind the confidence signal determines its structure in ways that should inform, not be assumed away by, the pipelines that rely on it.
