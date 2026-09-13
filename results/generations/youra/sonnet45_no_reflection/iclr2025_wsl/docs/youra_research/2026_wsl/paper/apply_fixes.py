#!/usr/bin/env python3
"""
Apply all 8 MAJOR fixes from Phase 6.5 Round 1 adversarial review
"""

import re

def apply_all_fixes(content):
    """Apply all MAJOR fixes systematically"""

    # MAJOR-1: Architecture embedding concatenation clarification
    content = content.replace(
        '$\\phi(\\mathbf{w}_i, \\mathbf{c}_a) = \\text{MLP}([\\mathbf{w}_i; \\mathbf{c}_a])$',
        '$\\phi(\\mathbf{w}_i, \\mathbf{c}_a) = \\text{MLP}([\\mathbf{w}_i; \\mathbf{c}_a])$ where $[;]$ denotes concatenation'
    )

    # MAJOR-2: "First systematic evaluation" → "To our knowledge"
    # Already fixed in lines 20, 28

    # MAJOR-3: Remove baseline comparison claims
    content = re.sub(
        r'\*\*Deep Sets \(Permutation-Invariant Baseline\)\*\*: We compare against',
        '**Deep Sets (Reference Point)**: Deep Sets [Zaheer et al., 2017] without explicit equivariance loss provides',
        content
    )
    content = content.replace(
        'Expected performance: ~40-50% zero-shot equivariance based on NFN\'s homogeneous results, providing a lower bound for our approach.',
        'Based on NFN\'s homogeneous results, we would expect ~40-50% zero-shot equivariance performance from this architecture on similar tasks, providing context for interpreting our 0% kernel robustness result.'
    )
    content = content.replace(
        '**Comparison to Expected Baselines**',
        '**Context from Expected Performance**'
    )
    content = content.replace(
        'While we did not implement comparison baselines due to early failure detection, we can contextualize',
        'While we did not implement comparison baselines due to early failure detection, we contextualize'
    )

    # MAJOR-4: Remove Johnson-Lindenstrauss misapplication
    content = re.sub(
        r'Extrapolating to real 100K-dimensional pretrained models using Johnson-Lindenstrauss bounds \(\$K = O\(\\log N / \\varepsilon\^2\)\$ for N=14K models, ε=0\.10\) suggests K~1000-2000 may be necessary',
        'Extrapolating to real 100K-dimensional pretrained models, this pattern suggests K~1000-2000 may be necessary',
        content
    )
    content = re.sub(
        r'\*\*Dimensionality bounds\*\*: Johnson-Lindenstrauss lemma provides lower bound:.*?Our K=32 is 30-60× too small\.',
        '**Dimensionality considerations**: Our K=32 choice proves inadequate.',
        content,
        flags=re.DOTALL
    )

    # MAJOR-5: Frozen-K interpretation - acknowledge marginal
    content = content.replace(
        'Frozen-K generalization marginally failed at 10.31%',
        'Frozen-K generalization failed marginally at 10.31%'
    )
    content = content.replace(
        'While marginal, this failure is directionally significant:',
        'While the 0.31pp gap is small and could reflect noise, when combined with t-SNE evidence showing strong architecture-specific clustering (Figure 2),'
    )

    # MAJOR-6: Contrastive learning - frame as speculative
    content = content.replace(
        '**Alternatives Not Tested**:',
        '**Alternatives Worth Exploring**:'
    )
    content = content.replace(
        'This provides stronger signal',
        'This could provide stronger signal'
    )
    content = content.replace(
        'This suggests successful approaches will require',
        'This suggests alternative approaches worth exploring may require'
    )

    # MAJOR-7: Early stopping interpretation
    content = content.replace(
        'Early stopping at 60% of planned epochs indicates optimization instability.',
        'Training stopped at 60% of planned epochs due to validation loss plateau.'
    )
    content = content.replace(
        'This suggests conflicting gradients—minimizing',
        'This pattern suggests possible gradient conflicts—minimizing'
    )
    content = content.replace(
        'This architectural tension supports the hypothesis that MSE-based equivariance loss is fundamentally incompatible with reconstruction objectives.',
        'Whether this represents fundamental incompatibility between the objectives or requires different hyperparameter tuning (higher λ_equiv, different optimization schedule) remains an open question for future work.'
    )

    # MAJOR-8: Reduce "negative result value" overclaiming
    content = content.replace(
        'Negative results are valuable when they provide clear failure modes and actionable alternatives. Our systematic analysis prevents the community from pursuing similar dead ends',
        'Our systematic analysis documents a specific dead end'
    )
    content = content.replace(
        'preventing the community from wasting effort on similar approaches',
        'documenting specific obstacles encountered with this approach configuration'
    )

    return content

def main():
    # Read original
    with open('/home/anonymous/YouRA_results_new_4_sonnet45_no_reflection/TEST_wsl_sonnet45_no_reflection_2/docs/youra_research/20260512_wsl/paper/06_paper.md', 'r') as f:
        content = f.read()

    # Apply fixes
    content = apply_all_fixes(content)

    # Write revised
    with open('/home/anonymous/YouRA_results_new_4_sonnet45_no_reflection/TEST_wsl_sonnet45_no_reflection_2/docs/youra_research/20260512_wsl/paper/06_paper_r1.md', 'w') as f:
        f.write(content)

    print("Revised paper written to 06_paper_r1.md")

if __name__ == '__main__':
    main()
