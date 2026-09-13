# Phase 6.5 Human Review Notes
**Generated:** 2026-03-15
**Round:** R1
**Note:** These issues require AUTHOR JUDGMENT — do NOT auto-fix.

| # | Issue ID | Category | Description |
|---|----------|----------|-------------|
| 1 | AC-4 | clarity | Abstract 0% qualification: Consider adding "(likely due to output format mismatch)" after "0% pass rate" in Abstract — author judgment on word count |
| 2 | AC-5 | clarity | L2 Limitations: Clarify that h-e1 *infrastructure* passed (15/15, 67/67) while h-e1 *gate metrics* failed — current L1 wording conflates both |
| 3 | AC-6 | clarity | Binomial formula: Confirm whether q in Var(r_ratio)=q(1-q)/T is per-test-case probability or per-rollout probability; add one explicit definitional sentence in Sec 3.1 |
| 4 | BR-3 | style | Abstract "production-ready infrastructure" — consider replacing with "validated at 15/15 tasks and 67/67 integration tests" for precision |
| 5 | BR-4 | formatting | Figure 3 simulation parameters (500 groups, q=0.45, T=5, G=8) should appear explicitly in Section 3.5 methodology so readers can reproduce |
| 6 | SE-3 | clarity | T=5 assumption: Add justification for using T=5 in tractability window analysis, or add one-row T-sensitivity table showing ρ at T=3,5,8 |
| 7 | SE-4 | style | "Hard prerequisite": Consider softening to "necessary prerequisite" or "required prerequisite" given the evidence comes from a single model/harness combination |
| 8 | SE-5 | formatting | 67 tests breakdown: Add parenthetical description of test categories (e.g., "67 integration tests covering prescreening pipeline, reward computation, and sandbox execution") |

## Round 2 Additional Items

| # | Issue ID | Category | Description |
|---|----------|----------|-------------|
| 9 | R2-HRN-1 | clarity | Introduction line ~39: "variance of R_ratio is q(1-q)/T" — confirm q is per-test-case probability; add definitional sentence linking q to the Binomial parameterization |
| 10 | R2-HRN-2 | formatting | Stale metadata note in Paper Statistics block references old "Liao et al." attribution warning — now obsolete after R1 fix; remove or update |
| 11 | R2-HRN-3 | formatting | "~72% pass@1 on HumanEval" claim (Section 5.3) has no citation source — add citation to Qwen2.5-Coder technical report (Hui et al., 2024, already in references) |
| 12 | R2-HRN-4 | clarity | SE-1 residual: Format-mismatch interpretation partially supported by HumanEval mention, but a brief note on why strict harness is necessary for GRPO training realism would strengthen the argument |
| 13 | R2-HRN-5 | clarity | 065_ground_truth.yaml peak_advantage field: "ρ ≥ 5× for q∈[0.3,0.55], T=5" was based on the pre-correction formula; after formula fix, update to reflect that ρ ≥ 5× holds for q∈[0.3,0.4] at T=5 |
