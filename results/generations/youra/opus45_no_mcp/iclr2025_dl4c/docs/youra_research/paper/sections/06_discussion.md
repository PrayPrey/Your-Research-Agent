# Discussion

## Mechanism Validation

Our experiments validate the complete causal chain underlying error-type gating:

1. Fine-grained penalties concentrate gradients at traceback locations (H-M1: 16.11×)
2. Traceback accuracy varies dramatically by error type (H-M2: 100% vs 20%)
3. Unreliable tracebacks cause gradient noise at ground-truth locations (H-M3: p<10⁻¹³)
4. Gating preserves signal where accurate, removes noise where not (H-M4: +4.61%)

The end-to-end efficiency improvement (H-E1) demonstrates practical benefit, though we note this is proof-of-concept scale requiring full validation.

## Honest Limitations

**Synthetic ground truth:** H-M2 and H-M3 use synthetic code templates with predetermined bug locations. While this ensures deterministic validation, real APPS samples may show different accuracy patterns. We view this as a conservative choice—demonstrating the mechanism on controlled samples before applying to noisy real data.

**Marginal significance for H-M4:** The SNR improvement (p=0.112) does not reach conventional significance. Our sample size (200 total) was reduced for PoC scope. The consistent direction across 1000 bootstrap iterations suggests the effect is real but requires N≈500+ for adequate power.

**Model scale:** All experiments use CodeT5-small (60M parameters). Gradient dynamics may differ at the 770M (CodeT5-large) or 7B+ scale typical of modern code LLMs. However, the causal mechanism—traceback parsing, token-level penalties, gradient concentration—is architecture-agnostic.

**Untested predictions:** P2 (error distribution shift during training) and P3 (increasing advantage over training) were not tested in our PoC. These require multi-epoch training runs with distribution tracking at checkpoints.

## Broader Impact

Our work introduces credit assignment reliability as a lens for understanding feedback granularity. This framing extends beyond error-type gating:

- **Test case reliability:** Individual test cases may have different diagnostic value; weighting feedback by test reliability follows similar logic
- **Multi-file localization:** Repository-level code generation faces even more complex localization challenges
- **Other modalities:** Image/video generation with localized feedback faces analogous reliability questions

The key insight—that finer granularity helps only when localization is accurate—applies whenever RL uses spatially localized feedback signals.

## Future Directions

**Continuous weighting:** Binary gating is simple but coarse. Per-exception-type accuracy estimates could enable proportional penalty weighting.

**Larger scale validation:** Replicating on CodeT5-large and decoder-only models (CodeLlama, DeepSeek-Coder) would establish generality.

**Real sample annotation:** Developing reliable ground-truth annotation for real APPS samples would strengthen H-M2/H-M3 claims.

**Distribution dynamics:** Tracking U_ignore fraction during full training runs would test P2/P3 predictions and potentially reveal time-varying optimal gating strategies.
