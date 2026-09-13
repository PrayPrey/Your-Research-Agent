# Related Work

## Direct Preference Optimization

Direct Preference Optimization (DPO) provides a closed-form solution for learning from human preferences without training a separate reward model. Given paired preferences (y_w, y_l) for prompt x, DPO optimizes:

$$\mathcal{L}_{\text{DPO}} = -\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)$$

This formulation has become the dominant approach for preference-based fine-tuning due to its simplicity and stability. However, DPO optimizes a single objective: matching human preferences. Our work asks whether auxiliary objectives can capture dimensions of response quality orthogonal to preference labels.

## Multi-Objective Extensions to DPO

Several works extend DPO with additional objectives. MODPO introduces margin-based auxiliary losses that provide additional training signal beyond binary preferences. PAMA (Pareto Multi-Objective Alignment) frames alignment as multi-objective optimization across multiple preference dimensions, demonstrating that DPO can accommodate multiple loss terms without destabilization. GAPO explores gradient-aware approaches to balancing conflicting objectives.

These methods share a common pattern: they add objectives derived from preference data (additional annotations, margin information, or decomposed preference dimensions). BiDPO differs by adding an objective orthogonal to preference labels—collaboration patterns that indicate how a response engages the user, not just whether users prefer it.

## Self-Play and Game-Theoretic Alignment

Self-Play Preference Optimization (SPPO) treats alignment as a two-player game, achieving strong performance through Nash equilibrium-based training. OAIF (Online AI Feedback) enables online preference learning from LLM annotators. These methods focus on improving preference optimization itself rather than adding orthogonal objectives.

## Human Agency in AI Systems

Mitelut et al. (2023) argue that intent-aligned AI may inadvertently deplete human agency by optimizing for immediate task completion rather than capability transfer. This theoretical framework motivates our empirical investigation: can we design training objectives that preserve agency-related patterns?

HCI research on collaborative dialogue identifies specific patterns associated with effective human-AI collaboration: explicit reasoning traces, uncertainty acknowledgment, and engagement invitations. We operationalize these patterns in our collaboration score heuristic.

## Gap Addressed

Prior multi-objective DPO extensions optimize for multiple dimensions of human preference. Prior work on human agency provides theoretical arguments without empirical validation in alignment training. No existing method combines DPO with an explicit agency-preservation objective derived from response-level patterns. BiDPO addresses this gap—though our results suggest the approach requires further development beyond PoC scale.
