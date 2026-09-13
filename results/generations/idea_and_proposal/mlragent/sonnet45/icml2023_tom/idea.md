# Title
Hierarchical Theory of Mind Modeling for Multi-Party Dialogue Systems with Recursive Belief Tracking

## Motivation
Current dialogue systems struggle with multi-party conversations where understanding requires reasoning about nested beliefs (e.g., "Alice thinks Bob doesn't know that Carol is upset"). While recent LLMs show basic ToM capabilities, they lack explicit mechanisms for tracking hierarchical mental states across multiple agents in dynamic conversations. This limitation hinders applications in collaborative AI, negotiation systems, and social robots where understanding complex interpersonal dynamics is crucial.

## Main Idea
I propose developing a **recursive belief state tracker** that explicitly models nested mental states in multi-party dialogues. The system would:

1. **Architecture**: Augment transformer-based dialogue models with a structured belief graph that maintains hierarchical representations of each agent's beliefs about others' mental states (up to n-th order ToM).

2. **Methodology**: 
   - Design graph neural networks to propagate belief updates when new information emerges
   - Train using synthetic data generated from multi-party scenarios with annotated belief states
   - Fine-tune on human conversations with implicit ToM reasoning tasks

3. **Expected Outcomes**: 
   - Improved performance on multi-party dialogue benchmarks requiring ToM
   - Better explanability through explicit belief state visualization
   - Enhanced ability to predict conversational breakdowns due to belief misalignments

4. **Impact**: Enable more natural human-AI collaboration in group settings and provide insights into computational mechanisms underlying social cognition.