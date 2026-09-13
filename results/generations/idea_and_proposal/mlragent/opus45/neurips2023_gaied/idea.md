# Title: Calibrated Uncertainty Signals for AI Tutors: Teaching Students When to Trust (and Doubt) Machine-Generated Explanations

## Motivation
Current generative AI tutors often present information with uniform confidence, regardless of accuracy, which can mislead students into accepting incorrect explanations or unnecessarily doubting correct ones. This is particularly dangerous in educational settings where students are building foundational knowledge and critical thinking skills. We need AI tutors that not only provide explanations but also communicate appropriate uncertainty levels, helping students develop healthy skepticism toward AI-generated content while still benefiting from AI assistance.

## Main Idea
We propose developing **Uncertainty-Aware Educational AI (UAEI)**, a framework that augments LLM-based tutors with calibrated confidence signals and metacognitive scaffolding. The methodology involves:

1. **Multi-source uncertainty quantification**: Combining semantic entropy, retrieval confidence from verified educational resources, and ensemble disagreement to estimate explanation reliability.

2. **Pedagogically-designed uncertainty communication**: Translating uncertainty scores into student-friendly cues (e.g., "I'm confident about this" vs. "Let's verify this together") that prompt verification behaviors without undermining trust.

3. **Adaptive verification prompts**: When uncertainty is high, automatically suggesting students cross-reference textbooks or consult instructors.

We will evaluate through controlled studies measuring (a) calibration quality, (b) student learning outcomes, and (c) development of critical AI literacy. This addresses both GAI→ED (improved tutoring) and ED→GAI (safeguarding against misinformation) while fostering AI-literate learners.