## Title
SRALT: Self-Validating Spaced Repetition Architecture for LLM Tutoring with Deep Knowledge Tracing

## Motivation
LLM-based tutoring systems show promise for personalized education but lack mechanisms for optimizing long-term retention and validating their own effectiveness. While Deep Knowledge Tracing (DKT) excels at mastery prediction (AUC=0.83) and spaced repetition enhances memory consolidation, current LLM tutors leverage neither. This creates a critical gap: students may perform well during sessions but forget material weeks later, with no system-level feedback to detect or correct this problem.

## Main Idea
We propose SRALT, a hybrid architecture combining DKT's predictive strength with LLM's dialogue capabilities. The core mechanism operates through four causal steps: (1) DKT processes interaction sequences to estimate concept-level mastery, (2) mastery predictions inform SM-2 algorithm-based review scheduling, (3) scheduled reviews trigger contextual LLM tutoring dialogues, and (4) delayed assessments validate DKT predictions while consolidating retention.

We will conduct a randomized controlled trial (n=100) in Python programming education, comparing SRALT against standard LLM tutoring. Primary prediction: 20%+ higher retention at 4-week intervals. Secondary prediction: DKT-retention correlation r>0.7, enabling self-validation. The architecture's key innovation is generating prediction-outcome pairs that allow continuous system calibration—addressing the fundamental challenge of building educational AI that can verify and improve its own effectiveness over time.