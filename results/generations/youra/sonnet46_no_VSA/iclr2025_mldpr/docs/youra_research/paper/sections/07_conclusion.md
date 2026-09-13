# 7. Conclusion

We set out to test a theoretically motivated hypothesis about benchmark lifecycle dynamics: that community breadth at benchmark introduction — the diversity of research teams participating in a benchmark when it first achieves plurality — predicts whether and how quickly that benchmark will be displaced. Both the lock-in mechanism (HR < 1: broad stakeholder investment → resistance to displacement) and the saturation mechanism (HR > 1: widespread adoption → perceived as solved → community-driven replacement) are supported by theory and case studies in the literature.

We operationalized community breadth as the count of distinct paper submissions per benchmark at plurality introduction year, constructed from the pwc-archive/evaluation-tables dataset (326k rows, CC-BY-SA-4.0). Before testing the mechanism, we applied a **5-gate FAIL FAST pre-validation protocol** that confirmed: (G0) 86.2% join coverage of h-e2 benchmarks, (G1) partial r² = 0.605 for the primary predictor's time-independence, (G2) partial r² = 0.975 for the secondary predictor's time-independence, (G3) std = 0.246 for adequate predictor variance, and (G4) max VIF = 2.14 with no multicollinearity. All five gates passed by wide margins.

On the h-e2 panel (258 complete-case rows, EPV ≈ 86), Cox proportional hazards regression yields:

> **HR = 1.006 (95% CI = [0.846, 1.196]), LRT p = 0.9495**

This is a near-perfect null. The diversity predictor adds ΔlogL = 0.0020 to the baseline model — essentially zero. Community breadth diversity at benchmark introduction year, as measured by paper submission count, explains none of the variance in plurality benchmark displacement timing. Both the lock-in and saturation mechanisms are falsified at this level of analysis.

**What this result rules in:** The 5-gate FAIL FAST protocol itself is a validated, reusable methodological contribution for benchmark lifecycle survival analysis — a pre-registration-equivalent rigor framework that separates data quality failure from hypothesis failure.

**What this result rules out:** Submission-count breadth as a predictor class for benchmark displacement timing in the Papers With Code ecosystem (2015–2023).

**What this result points toward:** Score trajectory (SOTA improvement velocity) remains the most promising untested predictor at full statistical power. Institutional diversity (team-deduplicated breadth, requiring author-level deduplication) is the most promising alternative operationalization of the breadth construct.

The community that builds benchmarks — and relies on them — benefits from understanding when benchmarks will be replaced. This paper contributes a negative result under optimal conditions: the most common feature used to characterize community adoption breadth does not predict replacement timing. The right predictor remains to be found.
