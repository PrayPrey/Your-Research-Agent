# Title
Semantic Consistency Graphs for Detecting and Quantifying Hallucinations in Multi-Turn LLM Conversations

## Motivation
Current hallucination detection methods primarily focus on single responses, missing the temporal inconsistencies that emerge across multi-turn interactions. In high-stakes domains like healthcare or legal advice, LLMs may contradict themselves across a conversation while maintaining high per-response confidence. This gap between instantaneous and longitudinal reliability poses serious risks for deployment, yet remains underexplored due to the computational challenges of tracking semantic coherence across extended dialogues.

## Main Idea
We propose constructing dynamic **Semantic Consistency Graphs (SCGs)** that represent claims and their relationships across conversation history. Each node represents an atomic claim extracted from LLM responses, with edges encoding semantic relationships (support, contradiction, independence). 

**Methodology**: (1) Use lightweight claim extraction models to parse responses into atomic statements; (2) Compute edge weights using efficient embedding-based similarity and natural language inference; (3) Apply graph-based anomaly detection to identify inconsistency clusters; (4) Aggregate local inconsistencies into conversation-level uncertainty scores.

**Expected Outcomes**: A scalable framework providing turn-by-turn uncertainty estimates with interpretable explanations highlighting specific contradictions. This enables users to identify when the model's knowledge boundaries are exceeded.

**Impact**: Enables safer deployment in conversational AI applications while establishing a new benchmark paradigm for evaluating hallucination across dialogue contexts rather than isolated responses.