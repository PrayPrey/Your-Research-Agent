## References

$$w_{\text{domain}} = \arg\max_{w} \mathbb{E}_{(i,j) \sim \text{Preferences}} \left[ \mathbb{I}(\text{score}_w(M_i) > \text{score}_w(M_j)) \right]$$

where $\text{score}_w(M) = \sum_{k=1}^{K} w_k \cdot \text{metric}_k(M)$ and $\sum w_k = 1$.

Expected domain-specific weights include:
- Healthcare: $w_{\text{fairness}} = 0.4, w_{\text{transparency}} = 0.35, w_{\text{performance}} = 0.25$
- Finance: $w_{\text{robustness}} = 0.45, w_{\text{consistency}} = 0.35, w_{\text{fairness}} = 0.20$
- Education: $w_{\text{alignment}} = 0.5, w_{\text{transparency}} = 0.3, w_{\text{accuracy}} = 0.20$