# Phase 6.5 R1 Changelog

## MAJOR-1: Fixed TRAK Results Table

**Location:** Section 5, "P3: TRAK Architecture-Invariance" table

**Before:**
| proj_dim=64 | 0.886 | 0.891 | 0.56% |
| proj_dim=256 | 0.923 | 0.922 | 0.11% |
| proj_dim=1024 | 0.951 | 0.947 | 0.42% |

**After:**
| proj_dim=64 | 0.941 | 0.944 | 0.36% |
| proj_dim=256 | 0.941 | 0.936 | 0.56% |
| proj_dim=1024 | 0.941 | 0.940 | 0.11% |

**Source:** 04_validation.md TRAK results

---

## MAJOR-2: Fixed TracIn Results Table

**Location:** Section 5, "P2: TracIn BERT Advantage" table

**Before:**
| 1 | 0.979 | 0.949 | +3.03% |
| 2 | 0.985 | 0.967 | +1.83% |
| 3 | 0.988 | 0.978 | +1.02% |

**After:**
| 1 | 0.979 | 0.949 | +3.03% |
| 2 | 0.977 | 0.963 | +1.42% |
| 3 | 0.976 | 0.965 | +1.13% |

**Source:** 04_validation.md TracIn results (Checkpoints 1,2,3 = Budget 64,256,1024)

---

## Summary

- 2 MAJOR issues fixed
- Both fixes align results tables with 04_validation.md source of truth
