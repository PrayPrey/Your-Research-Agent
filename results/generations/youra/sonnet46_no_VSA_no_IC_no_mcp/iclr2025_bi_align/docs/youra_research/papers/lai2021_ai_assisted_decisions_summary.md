# Paper Summary: Towards a Science of Human-AI Decision Making

**Authors:** Vivian Lai, Chenhao Tan (and related work group)
**Year:** 2021 (and related 2019-2022 series)
**Search term:** "Lai 2021 AI-assisted decision making human agency"
**Venue:** CHI / ACM conferences

## Key Contributions
- Systematic study of how AI assistance affects human decision quality and agency
- Measures "appropriate reliance": whether humans defer to AI when AI is correct and override when AI is wrong
- Identifies that AI confidence/explanation quality affects whether humans appropriately rely on AI or over-rely
- Framework distinguishes between: always-accept AI (automation bias), always-reject AI (algorithm aversion), and calibrated reliance

## Methodology
- Controlled user studies with lay participants making decisions with/without AI predictions
- Conditions: no AI, AI prediction only, AI prediction + confidence, AI prediction + explanation
- Outcome metrics: decision accuracy, AI agreement rate, switching rate (how often humans override AI)
- Domain: Recidivism prediction (COMPAS-style), income prediction, bird species classification

## Experiments & Results
- Human decision accuracy improves with AI assistance on average
- BUT: over-reliance rate is high (humans follow AI even when AI is wrong) — 60-80% agreement rate with AI regardless of AI accuracy
- Explanations help: saliency maps and feature importance reduce over-reliance by ~10-15%
- Critical finding: "appropriate reliance" is rarely achieved — humans either over- or under-rely
- The Human→AI alignment signal: appropriate reliance rate = fraction of decisions where human follows AI iff AI is correct

## Relevance to Gap 2
- Provides the Human→AI alignment proxy: "appropriate reliance" as a calibration metric
- Shows that AI output quality (AI→Human) does not automatically produce calibrated Human→AI alignment
- Directly operationalizes the Human→AI axis: appropriate reliance ∈ [0, 1], higher = better calibrated
- Dataset: Several decision-making studies with human behavioral data; some publicly available via OSF
- Limitation: domain-specific (recidivism, income); need to extend to NLP alignment context

## Phase 2A Discussion Role
Key dataset for Human→AI proxy: appropriate reliance rate from Lai et al. studies provides the Human→AI signal. Combined with AI→Human benchmark scores from RLHF papers, enables bidirectional gap computation. The gap hypothesis: as AI output quality (AI→Human) improves, does appropriate reliance (Human→AI) improve proportionally, or does over-reliance increase (automation bias)?
