# Phase 6.5 Changelog

## Round 1 Revisions

### M1: Ratio Inconsistency Fixed
- Location: Introduction paragraph 2 (line 17)
- Change: "7.56 times" -> "24.68 times"
- Location: Introduction paragraph 2 (line 17)
- Change: Added "(p=0.010)" after ratio for consistency
- Location: Introduction paragraph 4 (line 21)
- Change: "7.56x, p=0.027" -> "24.68x, p=0.010"

### M2: Statistical Caveat Added
- Location: Results Section 5.1 (after gap table)
- Change: Added sentence acknowledging single-run nature: "Note: These results represent single-run proof-of-concept experiments; multi-run replication with error bars is required for definitive statistical claims."

### M3: Causal Overclaim Softened
- Location: Abstract (line 9)
- Change: "supporting a *benchmark co-evolution* hypothesis" -> "consistent with a *benchmark co-evolution* hypothesis"
- Location: Conclusion (line 206)
- Change: "supporting a co-evolution hypothesis" -> "consistent with a co-evolution hypothesis"

### M4: Domain Confound Acknowledged
- Location: Discussion, Limitations section (limitation 1)
- Change: Expanded from "Two dataset pairs: Cannot claim generality across all domains" to include: "Additionally, CIFAR-10 (natural images) and SVHN (digits) represent fundamentally different visual domains; the observed gap difference may partially reflect domain-specific characteristics rather than popularity alone."

## Round 2 Revisions

### M1: Accuracy Values Corrected (Table 5.1)
- Location: Results Section 5.1, Table 5.1
- Change: Corrected accuracy values to match h-e1/04_validation.md ground truth
  - CIFAR-10: 94.86%/76.00% -> 87.92%/69.06% (gap 18.86% unchanged)
  - SVHN: 95.00%/97.35% -> 95.32%/97.68% (gap -2.35% unchanged)
- Note: Gap values (18.86%, -2.35%, 21.21pp) remain correct

### M2: H-M1 Methodology Clarification
- Location: Results Section 5.2, after Mann-Whitney p-value
- Change: Added clarification about different counting methodologies
- Note: 24.68:1 (p=0.010) confirmed as canonical from verification_state.yaml; 7.56:1 represents conservative keyword matching

## Round 2 Summary
- Issues fixed: 2
- Sections modified: Results 5.1 (Table), Results 5.2

## Cumulative Summary
- Total issues fixed: 6
- Sections modified: Abstract, Introduction, Results 5.1, Results 5.2, Discussion, Conclusion
