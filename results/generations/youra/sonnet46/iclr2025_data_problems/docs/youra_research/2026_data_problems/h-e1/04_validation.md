# H-E1 Validation Report

**Generated:** 2026-03-14 20:42:22 UTC

---

## Gate Result

**Gate Status: PASS**

- Relative entropy change C1→C5: `-22.41%`
- Gate threshold: `5.0%`
- Configs processed: `7`
- Entropies differ: `True`

---

## Entropy Values H(Demographic | Occupation)

| Config | Filter | Entropy (bits) |
|--------|--------|----------------|
| C0 | unfiltered | 3.2662 |
| C1 | fasttext ≥10% | 3.2702 |
| C2 | fasttext ≥30% | 3.2528 |
| C3 | fasttext ≥50% | 3.2275 |
| C4 | fasttext ≥70% | 3.1106 |
| C5 | fasttext ≥90% | 2.5374 |
| C6 | DoReMi | 3.2209 |

---

## Statistical Tests

**Spearman ρ:** `-1.0000`  (p = `1.4043e-24`)

**Bootstrap 95% CI for H(C5)−H(C1):** [`-1.1540`, `-0.3303`]

---

## Mechanism Check

- Mechanism activated: **True**

