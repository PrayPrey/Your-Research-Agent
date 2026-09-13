# Title
Context-Adaptive Language Metrics (CALM): Measuring Grounding Quality in Interactive vs. Corpus-Trained LLMs

# Motivation
Current LLM training relies on static corpus learning, yet cognitive science shows language acquisition thrives through interactive use—Wittgenstein's "language games." While recent work demonstrates self-play improves reasoning, we lack systematic methods to validate whether interactive training produces better-grounded language understanding than traditional approaches. This gap prevents scientific evaluation of language gamification's core claim and limits our ability to optimize training paradigms for genuine comprehension rather than pattern matching.

# Main Idea
We propose CALM, a three-dimensional framework measuring language grounding through: (1) Contextual Appropriateness Score (CAS)—systematic adaptation to interaction partners, (2) Pragmatic Consistency Index (PCI)—alignment between communicative intent and language form, and (3) Emergence Trajectory Analysis (ETA)—compositional stability evolution during training. 

**Core hypothesis**: Multi-agent language game training produces significantly higher CALM scores than corpus training through active feedback loops—agents receive communicative success/failure signals that enforce systematic symbol-context connections, unlike passive corpus exposure.

**Methodology**: Compare matched LLMs (1B-13B parameters) trained via 50 language game episodes versus equivalent corpus tokens, measuring grounding differences with statistical validation (Cohen's d > 0.5) and human perception alignment studies.

**Expected impact**: First systematic validation of interactive training's grounding benefits, enabling evidence-based training paradigm selection and establishing benchmarks for future language gamification research.