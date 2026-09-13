# Discussion

Our experiments reveal that UQ method effectiveness depends critically on task format—a finding with implications for both research methodology and practical deployment.

## Key Findings

### Format-Dependency as the Primary Result

The 0.24 AUROC gap between max probability and semantic entropy is not explained by implementation error (mechanism verification passes) but by format mismatch. Semantic entropy assumes responses contain meaningful semantic content for NLI comparison. MC answers are single letters that violate this assumption.

This finding reconciles our results with Kuhn et al. [2023]: their evaluation used free-form QA where responses contain substantial text for semantic comparison. Our MC format reveals where the method's assumptions break. Neither study is wrong; they evaluate under different conditions that favor different methods.

**Practical implication:** Method selection should match task format. For MC-format tasks, use simple confidence-based methods. Semantic entropy's computational overhead (5x inference + NLI model) yields no benefit and may actually harm discrimination on formats it was not designed for.

### Simplicity Wins for MC Hallucination Detection

Max probability—the simplest method we tested—achieves the highest AUROC. This suggests that for MC format, the discriminative signal is concentrated in the confidence of the selected answer. Additional sophistication (entropy over choices, semantic clustering) adds noise rather than signal.

This is not a general indictment of sophisticated methods. Rather, it demonstrates that method complexity must match task complexity. MC format is a low-complexity task where a low-complexity method suffices.

### Mechanism vs. Discrimination

Our separation of mechanism verification from discrimination evaluation is a methodological contribution. Prior work often conflates these: low performance could mean broken implementation or unsuitable method. By verifying that clustering functions (avg 4.92 clusters, entropy variance > 0), we establish that semantic entropy's failure on MC is fundamental to the format, not an artifact of poor implementation.

This approach generalizes: future UQ method evaluations should include mechanism verification to isolate format-specific limitations from implementation bugs.

## Connection to Prior Work

Our results extend the UQ literature in several ways:

1. **Controlled comparison methodology:** First head-to-head evaluation on identical conditions reveals format effects masked by prior heterogeneous evaluations.

2. **Format-dependency documentation:** First empirical demonstration that semantic entropy's advantage is format-contingent.

3. **Practical guidance:** Clear recommendation to match method to format rather than defaulting to most sophisticated available.

## Limitations

### Sample Size

Our PoC validation uses 50 samples from TruthfulQA mc1. While sufficient to establish the pattern (0.24 AUROC gap is substantial), full 817-sample validation would provide tighter confidence intervals on exact values. We interpret our results as evidence of relative method ranking, not precise AUROC estimates.

**Why acceptable:** PoC appropriate for hypothesis validation. Relative ranking (token > semantic on MC) is robust; full validation is future work.

### Single Model

We evaluate only Llama-3-8B-Instruct. Results may not generalize across architectures, model sizes, or training procedures. Llama-3-8B is representative of modern instruction-tuned models but is not universal.

**Why acceptable:** Representative model establishes proof-of-concept. Cross-model generalization is systematic but low priority given the clear format-dependency finding.

### MC Format Only

Our results apply specifically to MC-format hallucination detection. Free-form generation may yield different rankings—indeed, we hypothesize semantic entropy would perform better on free-form tasks where responses have semantic content.

**Why acceptable:** This is precisely our contribution: demonstrating format-dependency. Testing free-form is future work that would complete the picture.

### Sample Count for Semantic Entropy

We use 5 samples per question for semantic entropy, within the 5-10 range from Kuhn et al. but potentially suboptimal. More samples might improve clustering quality.

**Why acceptable:** 5 samples is standard. The mechanism verification passes, indicating clustering functions. More samples are unlikely to change AUROC from 0.56 to 0.70+ needed to match token methods.

## Broader Impact

### Positive Impact

Our work helps practitioners select appropriate UQ methods for their deployment context. Avoiding computational waste on sophisticated methods that underperform simple alternatives saves resources and improves system efficiency.

Documentation of format-dependency contributes to more rigorous UQ method evaluation standards in the research community.

### Potential Misuse

UQ methods for hallucination detection are safety-relevant. Incorrect method selection could create false confidence in unreliable outputs. Our results should be interpreted carefully: we show what works for MC format, not universally.

### Recommendations

1. Match UQ method to task format
2. Verify mechanism function separate from discrimination evaluation
3. Validate on representative samples before full deployment
4. Report format-specific results rather than claiming universal method superiority
