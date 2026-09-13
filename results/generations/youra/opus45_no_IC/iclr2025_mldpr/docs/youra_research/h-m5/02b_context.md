# Phase 2B Context: H-M5

**Hypothesis ID:** H-M5
**Type:** MECHANISM
**Statement:** Concentration-diversity cycle reinforces itself via positive feedback loop

## Full Statement
Under high concentration, if HHI increases year-over-year, then entropy decreases in subsequent year, because the positive feedback loop amplifies lock-in.

## Rationale
This is the core causal test—temporal precedence of concentration over diversity decline. Panel regression with lagged IV.

## Variables
- **IV:** ΔHHI_t (year-over-year HHI change)
- **DV:** ΔEntropy_{t+1} (subsequent year entropy change)
- **CV:** Venue FE, year FE, paper count

## Verification Protocol
1. Construct panel dataset: 21 venue-years with HHI and entropy
2. Run lagged panel regression: Entropy_t ~ HHI_{t-1} + venue FE + year FE
3. Run Granger causality test with 1-2 year lags
4. Check robustness with alternative lag structures

## Success Criteria
- **Primary:** β(HHI_{t-1}) < 0 with p < 0.05
- **Secondary:** HHI Granger-causes entropy (but not reverse)

## Gate Condition
- **Type:** SHOULD_WORK
- **If Fail:** ABANDON causal claim, report as correlation only

## Prerequisites
- H-M4 (COMPLETED, PASSED)

## Previous Hypothesis Results
H-M4 validated: Strong negative correlation (ρ=-0.958, p<0.001) between entropy and cross-benchmark variance. Effect confirmed in all 3 venues.

## Experimental Setup
- **Dataset:** Papers With Code Dataset-Paper Links
- **Model:** Lagged panel regression with fixed effects (statsmodels)
- **Source:** PWC API + cached data from H-E1

## Dependencies
- H-E1 data (HHI/entropy per venue-year)
- H-M4 validation results
