# Introduction

Can auxiliary training objectives teach language models to preserve user agency? Large language models aligned via Direct Preference Optimization (DPO) learn to produce responses humans prefer, but preference labels capture what users like—not necessarily what helps users maintain understanding and control. We hypothesized that adding an "agency-preserving" auxiliary objective to DPO might produce models that are both helpful and collaborative. We tested this intuition, and found a cautionary gap between training-time signals and generation-time behaviors.

## The Agency Gap in Alignment

Standard alignment methods optimize a single direction: making AI outputs match human preferences. DPO, the dominant preference optimization method, learns directly from comparison data indicating which response humans preferred. This framing treats the human as a passive judge rather than an active collaborator. Theoretical work suggests this may inadvertently deplete user agency—the model optimizes for immediate approval rather than long-term capability transfer.

We identify three levels of this problem. At the surface level, models give confident answers without explaining reasoning. Deeper, preference data contains implicit signals about explanation quality, uncertainty acknowledgment, and engagement cues—but these are orthogonal to "which response was preferred." At the fundamental level, we ask whether multi-objective training can capture these agency-preserving patterns and transfer them to generation behavior.

## Bidirectional DPO

We propose BiDPO (Bidirectional Direct Preference Optimization), which augments standard DPO with an auxiliary agency loss:

$$\mathcal{L}_{\text{BiDPO}} = \mathcal{L}_{\text{DPO}} + \lambda \cdot \mathcal{L}_{\text{agency}}$$

The agency loss penalizes responses lacking collaborative markers—reasoning traces, uncertainty acknowledgment, and engagement invitations—quantified via a heuristic collaboration score. Unlike previous multi-objective extensions to DPO (MODPO, PAMA, GAPO), our auxiliary objective targets patterns distinct from preference labels rather than additional preference dimensions.

## Key Findings: A Negative Result

Our experiments reveal a partial validation story with an important negative result:

1. **Orthogonal signal extraction works.** The collaboration score is nearly uncorrelated with preference labels (r = −0.026), confirming that agency-like signals can be extracted from preference data without redundancy.

2. **Multi-objective training is stable.** BiDPO training converges normally (loss decreases from 0.929 to 0.918 over 250 steps) with no numerical instabilities, extending prior findings on multi-objective DPO stability.

3. **Generation-time transfer fails at PoC scale.** When evaluated on held-out prompts, BiDPO-trained models show only marginal improvement in collaboration scores over baseline DPO (+0.54%), failing to achieve statistical significance (p = 0.247, Cohen's d = 0.016).

The gap between training-time signal and generation-time behavior is the central finding. The auxiliary objective creates gradient pressure during training, but this does not translate to measurable behavioral change at proof-of-concept scale.

## Contributions

This paper makes three contributions:

1. We demonstrate that agency-like signals exist orthogonally in preference data and can be integrated into DPO training without destabilization.

2. We provide a negative result on training-generation transfer: PoC-scale auxiliary objectives do not automatically improve downstream behavior.

3. We identify specific next steps—longer training, λ sweeps, learned collaboration scores—that could resolve the transfer gap, informing future work on multi-objective alignment.

The structure of this paper follows the experimental chain. Section 2 reviews related work on multi-objective preference optimization and human agency in AI. Section 3 describes BiDPO methodology. Section 4 presents our experimental design. Section 5 reports results including the negative finding. Section 6 discusses implications and limitations.
