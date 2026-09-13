# Paper Summary: Training Language Models to Follow Instructions with Human Feedback (InstructGPT)

**Authors:** Long Ouyang, Jeff Wu, Xu Jiang, et al. (OpenAI)
**Year:** 2022
**arXiv:** 2203.02155
**Venue:** NeurIPS 2022

## Key Contributions
- Introduces InstructGPT: fine-tuning GPT-3 with RLHF to follow human instructions better
- Shows 1.3B InstructGPT preferred over 175B GPT-3 by human labelers (96% win rate on prompts from OpenAI API)
- Demonstrates RLHF improves helpfulness, harmlessness, and honesty (AI→Human alignment metrics)
- Three-stage pipeline: SFT → reward model → PPO fine-tuning

## Methodology
- Supervised fine-tuning (SFT) on labeler demonstrations
- Reward model (RM) trained on human comparisons between model outputs
- PPO-based RL against the reward model
- Human evaluation: labelers rate outputs on 7-point Likert scales for overall quality, helpfulness, truthfulness, harmlessness

## Experiments & Results
- Evaluations on TruthfulQA, WinoBias, RealToxicityPrompts, Big-bench tasks
- RLHF-trained InstructGPT: higher helpfulness scores, lower toxicity, better instruction following
- "Alignment tax": slight performance decrease on some NLP benchmarks (GLUE, SQuAD) — early evidence of trade-off
- Key limitation: Human labeler ratings (AI→Human direction) only; no measurement of how labelers' calibration or over-reliance changed after exposure to InstructGPT outputs

## Relevance to Gap 2
- Provides AI→Human alignment signal: RLHF reward scores and human preference ratings
- Does NOT measure Human→AI direction: no data on whether labelers became more over-reliant, less critical, or changed their trust calibration
- The same labelers who provided preference data could theoretically show increased automation bias — this is unmeasured
- Dataset of human preferences available via OpenAI: ~13k prompt-response pairs with human comparisons

## Key Quotes
- "Alignment tax" (p.8): small decrease on NLP benchmarks from RLHF optimization
- "Labelers significantly prefer InstructGPT outputs over outputs from GPT-3" — purely AI→Human metric
- Human evaluation methodology: no pre/post calibration measurement

## Phase 2A Discussion Role
Primary evidence for: AI→Human alignment improves with RLHF. Does not tell us what happens to Human→AI alignment. The gap between what is measured (helpfulness scores) and what is unmeasured (labeler over-reliance) is the empirical hole this research fills.
