# 6. Discussion

## 6.1 Why the Proxy Failed

Canonical HumanEval solutions are carefully crafted reference implementations. They pass all tests by design and follow Python conventions. In contrast, LLM-generated code—especially early attempts in a repair loop—contains more issues:

- **Undefined variables:** LLMs may reference variables before definition
- **Type mismatches:** Without type annotations, type errors appear at runtime
- **Incomplete logic:** First attempts often miss edge cases
- **Import issues:** LLMs may import unused libraries or miss required ones

Using canonical solutions as an LLM proxy conflates the reference answer with the model's attempts. The 9.15% warning rate reflects human code quality, not LLM generation behavior.

## 6.2 What the Baseline Tells Us

Despite the proxy limitation, our results provide value:

1. **Floor established:** Canonical solutions have ~9% warning rate. LLM code should exceed this, providing room for the static analysis intervention to act.

2. **Pipeline validated:** The pylint analysis infrastructure works. Components are reusable for future work with LLM API access.

3. **Warning types identified:** The 9 warning categories (bad-indentation, unused-import, bare-except, etc.) are actionable for code repair. They explain *why* code is problematic.

## 6.3 Gate Design Implications

The MUST_WORK gate served its purpose. Had we skipped the existence check and proceeded to full pass@k evaluation, we would have:
- Wasted compute on the wrong code source
- Produced results that don't test the hypothesis
- Potentially drawn incorrect conclusions

Gate-based validation catches methodology issues early. The 30% threshold was chosen based on the hypothesis that static analysis needs sufficient signal to be useful—if most code has no warnings, the intervention adds noise.

## 6.4 Limitations

**Primary:** No LLM-generated code tested. API access unavailable during this study.

**Secondary:**
- Single dataset (HumanEval only, not MBPP)
- Single static analyzer (pylint, not mypy)
- Single severity filter configuration

**Framing:** This is a methodology study establishing baseline and validating infrastructure—not a full hypothesis test.

## 6.5 Path Forward

To complete the hypothesis evaluation:

1. **Re-run h-e1 with LLM API:** Generate code using GPT-4 or Claude, measure warning rates
2. **If h-e1 passes:** Proceed to h-m1 (LLM interprets warnings) and h-m2 (non-overlapping errors)
3. **Full evaluation:** Compare pass@k between static+execution vs. execution-only conditions

The pipeline, baseline, and methodology are ready. The missing ingredient is LLM API access.
