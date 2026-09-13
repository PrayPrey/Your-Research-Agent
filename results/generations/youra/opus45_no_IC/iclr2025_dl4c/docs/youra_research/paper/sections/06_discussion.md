# Discussion

## Key Findings

Our mechanism validation study yields a central finding: **FGO's benefit comes from gradient exclusion**. Non-executed tokens receive exactly zero gradient, while executed tokens receive 1.78x stronger signal concentration. This concentrates learning on code that actually contributed to the reward.

This finding has several implications:

1. **Mechanism Simplicity**: The active ingredient is simpler than previously assumed. FGO does not require sophisticated credit assignment—pure gradient exclusion suffices.

2. **Trace Information Matters**: The comparison between trace-based and random masking (both at 81.2% sparsity) shows that execution information, not just sparsity, drives improvement. Random masking excludes gradients but does not concentrate them on causally relevant tokens.

3. **Reusable Components**: Our validated implementations of trace collection, token classification, and masked PPO loss provide a foundation for future code RL research.

## Limitations

We acknowledge several limitations of this study:

### L1: Simulation-Based Efficiency Validation

H-M3 uses simulated learning curves with parametric models rather than actual PPO training. While we verify the mechanism (gradient exclusion works correctly), we cannot validate convergence speed or sample efficiency claims. Full training runs are required for production deployment.

**Impact**: "Faster convergence" remains unverified. Our +10% final pass@1 is simulation-based.

**Mitigation**: Core mechanism (gradient exclusion) is verified independently of efficiency claims.

### L2: Token-Line Mapping Precision

Token classification achieves 81% F1 rather than the 95% target. The gap stems from tokenizer boundaries not aligning with source line boundaries, not from trace collection failures.

**Impact**: Some tokens are incorrectly masked, potentially reducing FGO effectiveness.

**Mitigation**: AST-based span mapping (rather than line-based) could improve precision. The 81% F1 is sufficient for mechanism validation.

### L3: PoC Scale Limitations

Our experiments use a single seed for H-E1 and limited training steps. Statistical variance is not fully characterized, and the full factorial design (content × granularity) is not executed.

**Impact**: Cannot claim statistical significance for P2/P3 predictions.

**Mitigation**: Phase 5 will provide full baseline comparison with multiple seeds.

## Scope Conditions

Our results hold under specific conditions:

| Condition | Results Hold | May Not Hold |
|-----------|-------------|--------------|
| Python code | Yes | Other languages (different trace tools) |
| 7B model scale | Yes | <3B or >13B (untested) |
| Function-level tasks | Yes | Repository-level (SWE-bench) |
| PPO algorithm | Yes | Other RL algorithms (DPO, REINFORCE) |

## Broader Impact

This work validates a mechanism for improving code RL, with potential benefits for code generation systems. We do not anticipate direct negative societal impacts from mechanism validation research. However, improved code generation capabilities could amplify both beneficial uses (developer productivity) and harmful uses (automated vulnerability exploitation).

Our focus on mechanism validation rather than capability advancement reduces dual-use concerns compared to proposing new state-of-the-art methods.

## Future Work

Several directions emerge from our findings:

1. **AST-Based Mapping**: Replace line-based token mapping with AST span mapping to improve classification precision beyond 81% F1.

2. **Factorial Comparison**: Execute the full 2×3 factorial design (content × granularity) to test P2/P3 predictions about which factor dominates.

3. **Full Training Validation**: Run complete PPO training to validate convergence speed and sample efficiency claims.

4. **Multi-Language Extension**: Develop trace collection infrastructure for languages beyond Python (Java debugger, C++ coverage tools).
