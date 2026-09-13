# Methodology

Given the gap between the PEFT community's assumptions and Mamba's architecture, we designed experiment h-e1 as a **MUST_WORK existence check** — a protocol that gives projection-only LoRA every possible advantage and treats failure as an unambiguous signal rather than a tuning problem. The design philosophy is: if LoRA is going to work on Mamba for classification at all, it should work under the conditions we construct. If it does not, the failure mode is architectural, not configurational.

The key diagnostic insight that shaped the methodology: we measured **per-epoch accuracy alongside loss** at every training epoch. This decision, which seems routine, is the methodological contribution that makes the failure visible. Loss curves can look plausible — oscillating, non-zero, apparently "doing something" — while accuracy reveals complete learning failure. Three consecutive identical accuracy values across epochs cannot be rationalized as slow convergence or unlucky initialization.

## Mamba Architecture: Selective State Space Scan and Gradient Flow

Understanding the methodology requires understanding what sits between the classification head and the LoRA weight matrices in a Mamba model.

Mamba-130m (model identifier: `state-spaces/mamba-130m-hf`) is a 24-layer causal language model with hidden dimension `d_model = 768`, inner dimension `d_inner = 1536` (expansion factor 2), state dimension `d_state = 16`, and discrete-time rank `dt_rank = 48`. Each layer contains a MambaBlock with the following `nn.Linear` projection layers: `in_proj` (768 → 3072, projecting to x/z/input), `out_proj` (1536 → 768, projecting SSM output back to residual), `x_proj` (1536 → 112, projecting to dt/B/C parameters), and `dt_proj` (48 → 1536, expanding the discrete-time parameter).

The MambaBlock also contains a `conv1d` layer (not `nn.Linear`) and, critically, the **selective SSM scan**: the computation `h_t = Ā(Δ, A)·h_{t-1} + B̄(Δ, B)·x_t`, `y_t = C·h_t`, where A, B, C are derived from the x_proj output and Δ is derived from x_proj + dt_proj. This scan is implemented as a custom CUDA parallel associative scan (`selective_scan_cuda`), not via standard PyTorch autograd primitives.

The gradient path for a classification loss placed on the final hidden state runs: `classification_head → final hidden state → (through scan and projection layers of all 24 layers) → LoRA weight matrices`. The SSM scan sits *between* the classification head and the LoRA targets in every layer. For the model's pretraining task (next-token prediction), this backward path through the scan is well-exercised and numerically stable. For a randomly-initialized classification head computing sequence-level predictions, the backward path is novel — and as our experiments demonstrate, apparently ineffective at communicating task-discriminative signal to the LoRA matrices.

The `conv1d` layer is excluded from LoRA targets because it is not `nn.Linear` and would cause PEFT installation errors. The `dt_proj` layer was excluded from our primary configuration (Condition A) because it represents an SSM-adjacent parameter that could be considered "inside" the scan computation; including it while also OOM-ing on an H100 NVL (documented in version v9) established a practical boundary. The `dt_proj` exclusion is consistent with the standard community configuration for Mamba projection-only LoRA.

## LoRA Application to Mamba-130m

We applied LoRA using the HuggingFace PEFT library (v0.9+) with the following configuration, matching the community reference (alxndrTL/mamba-peft, 2024):

| Hyperparameter | Value | Rationale |
|---|---|---|
| Target modules | `in_proj`, `out_proj`, `x_proj` | Standard Mamba-1 projection LoRA; community reference configuration |
| Rank (r) | 8 | Standard for classification fine-tuning; referenced in MambaPEFT |
| Alpha (α) | 16 | 2r; standard scaling factor |
| Dropout | 0.05 | Standard regularization |
| Trainable parameters | 1,484,288 (1.14% of 130M) | Confirmed by PEFT `print_trainable_parameters()` |

**Rationale for this configuration:** We chose the most commonly referenced Mamba LoRA setup — the one a practitioner would apply based on community documentation — to test whether this configuration produces learning at all. An existence check should use the configuration most likely to succeed; if the standard community configuration fails, the field needs to know. Testing exotic configurations before establishing the standard one fails would invert the proper order of investigation.

The LoRA adapters are installed into all 24 MambaBlocks. LoRA keys appear in the model state dictionary (e.g., `backbone.base_model.model.layers.0.mixer.in_proj.lora_A.default.weight`), confirming installation. The classification head is a single `nn.Linear(768, num_labels)` layer, applied to the last-token hidden state from the final MambaBlock output.

**Classification head design:** Last-token pooling over the final hidden state is the standard approach for causal LMs adapted to classification — it is the token most likely to encode sequence-level information given the model's left-to-right attention structure. The head is randomly initialized; no special initialization (orthogonal, scaled, etc.) is applied, consistent with standard practice and with the goal of testing the standard approach rather than an optimized variant.

## GLUE Fine-Tuning Setup

We fine-tune separately on each GLUE task using the following shared training protocol:

| Hyperparameter | Value | Source |
|---|---|---|
| Optimizer | AdamW | Standard for LoRA |
| Learning rate | 3×10⁻⁴ | Phase 2B; MambaPEFT reference; standard for LoRA |
| Weight decay | 0.01 | Phase 2B |
| Batch size | 32 | Phase 2B; MambaPEFT reference |
| Epochs | 3 | Existence PoC protocol (see rationale below) |
| LR schedule | Linear warmup (6%) + linear decay | Standard HF Trainer default |
| Seed | 42 | Single seed; architectural failures are not seed-sensitive |
| Training samples | 4,000 (subsampled from train split) | Existence PoC protocol |
| Max sequence length | 128 tokens | Covers SST-2/MNLI sentence pairs |
| Tokenizer | GPT-NeoX-20B tokenizer (50k vocab) | Standard for `mamba-130m-hf` |

**Why SST-2 and MNLI:** SST-2 is the primary gate task — binary sentiment classification with an established, easily interpretable baseline (majority class ≈ 50%). It is the task used in the MambaPEFT reference, making it the natural comparison point. MNLI adds a second task with different structural demands: three-class natural language inference requiring understanding of sentence-pair entailment relationships, with a three-class baseline near chance (33%). If LoRA fails on both SST-2 (binary, sentiment) and MNLI (three-class, inference), the failure is cross-task and not an artifact of the specific classification structure.

The combination is particularly diagnostic because MNLI failure can reveal not just absence of learning but active degradation — the model being pushed toward a degenerate prediction regime. SST-2 failure reveals flat learning; MNLI failure reveals negative transfer. Together, they characterize the gradient barrier failure mode more completely than either task alone.

**Why 3 epochs, 4,000 samples:** An existence check is designed to detect whether a method can learn at all, not to measure its ceiling performance. Three epochs of 4,000 samples is sufficient for LoRA to converge on SST-2 with transformer architectures — it is a setting where success, if achievable, would be visible. Using more data or more epochs for a method that is not learning would not change the conclusion; it would only waste compute. Conversely, using fewer epochs risks conflating genuine gradient barrier failure with an insufficient number of gradient steps. Three epochs provides a clear window: long enough to see convergence if it occurs, short enough to be efficient if it does not.

**MUST_WORK gate criterion:** We defined a conservative pass criterion: SST-2 accuracy > 70% after three epochs. The conservatism is deliberate. The community reference reports 90–92% — a 70% gate gives LoRA substantial benefit of the doubt, allowing for differences in training setup that might cost 20 percentage points of performance while still demonstrating meaningful learning from the 49.1% zero-shot baseline. A gate of 90% would unfairly penalize any training recipe differences; a gate of 70% accepts that the setup may be suboptimal while still requiring demonstrable learning (a 21 percentage-point lift from zero-shot).

## Diagnostic Methodology

Our core diagnostic design choice was **per-epoch accuracy measurement**, not just loss monitoring. This choice is what reveals the gradient barrier.

Loss curves can exhibit several patterns consistent with either learning or non-learning:
- Monotonically decreasing loss → likely learning
- Oscillating loss (no trend) → ambiguous without accuracy data
- Non-zero loss throughout training → consistent with either gradient flow or gradient barrier

Accuracy is the authoritative criterion because it measures task performance directly. Three consecutive identical accuracy values across epochs eliminate all alternative explanations:
- Slow convergence would produce monotonically increasing (if slow) accuracy
- Lucky initialization plateau would not survive three consecutive identical values
- Seed sensitivity would produce variation across epochs as the model samples different batches

We evaluate accuracy on the full validation split at the end of each epoch: SST-2 validation (872 examples), MNLI matched validation (9,815 examples). We also log cross-entropy loss per training batch to characterize the optimization trajectory independently of task accuracy. The combination of both signals — per-epoch accuracy and per-batch loss — provides the complete diagnostic picture.

**Zero-shot evaluation as baseline:** Before any fine-tuning, we evaluate the base Mamba-130m model (no LoRA, no classification head training) on each GLUE task using lm-evaluation-harness with multiple-choice prompting. This establishes the reference: what does Mamba-130m achieve without any adaptation? The zero-shot baseline is measured independently from the fine-tuning experiments to ensure the comparison is clean.

The zero-shot evaluation uses a different paradigm than the fine-tuning evaluation: lm-evaluation-harness presents GLUE tasks as multiple-choice completions scored by the model's language modeling probability, while fine-tuning evaluation uses a classification head on the final hidden state. This paradigm mismatch is a limitation we acknowledge — a perfect zero-shot comparison would use the same evaluation head as the fine-tuning evaluation — but it does not affect the primary conclusion, which rests on the *within-fine-tuning* comparison: whether three epochs of training produce any improvement in accuracy over epoch 0, regardless of the zero-shot reference method.

**Implementation correctness verification:** Before accepting any experimental result, we verify that LoRA is installed correctly: (1) LoRA keys (`lora_A`, `lora_B`) exist in the model's state dictionary at the expected module paths, (2) the LoRA weight matrices are non-zero after training (confirming that gradients were computed and parameter updates occurred), and (3) the trainable parameter count matches the expected value for rank 8 on the targeted modules. All three checks pass in our experiments — the LoRA adapter is installed, receives gradients, and its weights are updated. This is what makes the result informative: the failure occurs downstream of correct installation, in the gradient signal that reaches the adapters, not in the installation itself.
