# Human Review Notes

**Date**: 2026-08-31
**Rounds Completed**: 1
**Source Review**: paper/review/065_review_r1.md (Part 4: Human Review Notes)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Citation gap | 1 |
| Implementation check | 1 |
| Framing clarity | 1 |
| Typesetting | 1 |
| Protocol transparency | 1 (RESOLVED in paper — marked below) |
| Arithmetic formatting | 1 (RESOLVED in paper — marked below) |
| Precision | 1 |
| Scope claim | 1 |
| Citation hygiene | 2 |
| Presentation | 1 (RESOLVED in paper via placeholders) |
| Methodological robustness | 1 (RESOLVED in paper — marked below) |
| **Total** | **12** |

---

## Round 1 Issues

### Citation Gap

**[MINOR-CIT-1]** §1.1, para 2 — "a protocol sufficient for LoRA to converge on SST-2 with transformers" is stated as fact but not cited. Add one citation (e.g., Hu et al. 2022 Table 2 convergence epochs, or a transformer LoRA benchmark paper that shows 3-epoch SST-2 convergence).

**Location**: §1.1, second paragraph in Introduction  
**Action needed**: Add citation or narrow the claim to "typical for LoRA on transformers [citation]."

---

### Implementation Check

**[MINOR-IMPL-1]** §3.2, last para — State dict key cited as `backbone.base_model.model.layers.0.mixer.in_proj.lora_A.default.weight`. Verify this exact path matches the actual PEFT v0.9+ output for `mamba-130m-hf`. The PEFT key path structure changed across library versions and the exact prefix (`backbone` vs. `model`) should be confirmed against the actual saved checkpoint from v8.

**Location**: §3.2, state dict key example  
**Action needed**: Run `print([k for k in model.state_dict().keys() if 'lora_A' in k][:2])` on the v8 checkpoint and update the example key if it differs.

---

### Framing Clarity

**[MINOR-FRAME-1]** §4.2 — The section states "QNLI and QQP were planned but not evaluated" while §1.4 Contributions says the baselines for all four tasks are documented. This is technically consistent (Table 1 includes zero-shot baselines for all four tasks; the QNLI/QQP *fine-tuning* was not completed) but could confuse readers who don't track the zero-shot vs. fine-tuning distinction across sections. Consider adding a parenthetical in §4.2 clarifying: "QNLI and QQP zero-shot baselines are documented in Table 1; only fine-tuning was not completed."

**Location**: §4.2, QNLI/QQP note  
**Action needed**: Add parenthetical clarification.

---

### Typesetting

**[MINOR-TYPE-1]** §5.2 Table 2, "vs. Gate" column — Computed values (−0.2092, −0.1908) should be confirmed to render correctly in LaTeX without floating-point formatting artifacts. The values are exact subtractions (0.70 − 0.4908 = 0.2092; 0.70 − 0.5092 = 0.1908) and display cleanly in Markdown, but LaTeX rendering with `siunitx` or standard `tabular` should be verified.

**Location**: §5.2, Table 2  
**Action needed**: Test LaTeX rendering before submission.

---

### Protocol Transparency

**[RESOLVED in r1]** §5.3 — "MNLI training was halted after epoch 2 due to the monotonically worsening trend" — whether this was pre-specified or adaptive was unclear. **RESOLVED**: r1 adds explicit statement that the halt was an adaptive (not pre-specified) decision, noted for transparency.

---

### Arithmetic Formatting

**[RESOLVED in r1]** §5.5 — "125 gradient steps per epoch (4,000 samples / batch size 32 × 3 epochs)" — the parenthetical was ambiguous (operator precedence unclear). **RESOLVED**: r1 rewrites to "125 gradient steps per epoch (4,000 samples / batch size 32; 375 steps total across 3 epochs)."

---

### Precision

**[MINOR-PREC-1]** §6.1 (original), last paragraph — "The SSM scan allows noise but not signal to pass backward" — this is a vivid metaphor but mechanistically imprecise. Gradient barriers in standard autograd typically block ALL backward signal. The claim that noise passes but discriminative signal doesn't is a specific causal claim that isn't directly measured. **Note**: r1 has significantly rewritten this paragraph to introduce the "partial barrier" framing; this note remains for human review to confirm the new wording ("passes noise but not signal") has been sufficiently softened throughout. Preferred language: "the updates carry non-discriminative gradient signal" rather than "noise passes through."

**Location**: §6.1, partial barrier paragraph in r1  
**Action needed**: Scan all instances of "noise" as a gradient metaphor and confirm none assert it as a mechanistic claim beyond the hedging already added.

---

### Scope Claim

**[MINOR-SCOPE-1]** §6.4 — "Falcon-Mamba, Jamba, Zamba2" are listed as SSM-family models expected to share the gradient barrier concern. Verify these models actually use the same `selective_scan_cuda` kernel (vs. pure PyTorch SSM implementations or Triton rewrites). The generalization is structurally plausible but architecturally non-trivial — Jamba and Zamba2 are hybrid transformer/SSM architectures and may have different backward-pass properties than pure SSM Mamba-1.

**Location**: §6.4, last paragraph  
**Action needed**: Add a qualifier such as "architecturally related models that share the selective scan mechanism" or verify kernel lineage per model.

---

### Citation Hygiene

**[MINOR-CIT-2]** Sinha et al. 2021 — marked [UNVERIFIED] in ground truth. arXiv ID (2104.08691) is from an inferred source and must be verified before submission. The reproducibility community framing in §2.5 does not require this specific citation — ReScience (https://rescience.github.io/) could substitute and is more easily verified.

**Location**: References, Negative Results section  
**Action needed**: Verify arXiv:2104.08691 is Sinha et al. ML Reproducibility Challenge 2020, or replace with ReScience citation.

**[MINOR-CIT-3]** lm-evaluation-harness — version number not pinned in the reference. Ground truth notes "version pinned to experiment environment" but the reference only says "Version 0.9+." For reproducibility, add the exact version tag used (e.g., v0.4.x) as retrieved from the experiment environment's pip freeze or conda list.

**Location**: References, Evaluation Tooling section  
**Action needed**: Pin exact version tag in citation.

---

### Methodological Robustness

**[RESOLVED in r1]** §3.4 — "Three consecutive identical accuracy values eliminate all alternative explanations" listed three alternatives. A fourth alternative (evaluation bug: same checkpoint evaluated each time) was noted by the reviewer. **RESOLVED**: r1 adds the fourth alternative and its refutation (evaluation confirmed as a per-epoch callback; LoRA weight values differ between epochs confirming distinct model states).

---

### Presentation

**[MINOR-PRES-1 — partially resolved]** 0 figures is highly unusual for an 8-page ICML submission. r1 adds [Figure 1] and [Figure 2] placeholders with descriptions, but actual figures must be generated before submission. Recommended: (1) a Mamba architecture diagram showing the gradient path with SSM scan barrier annotated; (2) a 2-panel accuracy curve (SST-2 flat line + MNLI degradation). These can be generated with matplotlib from the tabular data already in the paper — no new experiments required.

**Location**: Figures section (currently 0 actual figures)  
**Action needed**: Generate Figures 1 and 2 from tabular data; replace placeholders with actual figure references and captions.
