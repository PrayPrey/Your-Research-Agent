## References

- $\mathcal{L}_{\text{diversity}} = -\mathbb{E}_j[H(\pi_j)]$ encourages non-degenerate mixture weights (entropy regularization)

**Stage 3: Fine-tuning with Policy Feedback (Epochs 51-100)**
1. Deploy policy $\pi_\theta$ trained with reward model $R_\theta$
2. Collect human feedback on policy outputs
3. Fine-tune all components end-to-end with policy gradient signals