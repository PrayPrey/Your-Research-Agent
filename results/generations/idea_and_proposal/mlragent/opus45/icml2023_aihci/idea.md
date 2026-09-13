# Title: Interactive Error Correction for UI Generation through Natural Language Dialogue

## Motivation
Current AI-powered UI generation systems often produce outputs that require multiple iterations to meet user expectations, yet they lack effective mechanisms for users to communicate specific corrections. Users typically must either accept suboptimal results or completely regenerate outputs, wasting computational resources and user effort. This disconnect between generation capability and user intent refinement represents a critical gap in human-AI collaboration for creative tasks. Enabling intuitive, dialogue-based error correction would make UI generation more practical and accessible to non-technical users.

## Main Idea
We propose a **Dialogue-Guided UI Refinement (DGUR)** framework that allows users to iteratively correct generated UIs through natural language feedback. The system combines:

1. **A grounded correction parser** that maps natural language critiques (e.g., "make the button larger and move it to the right") to specific UI element modifications using a fine-tuned vision-language model.

2. **A hierarchical edit memory** that tracks correction history to prevent regression and learn user preferences across sessions.

3. **An uncertainty-aware generation module** that highlights ambiguous regions, proactively asking users for clarification before committing changes.

We will create a benchmark dataset of UI correction dialogues through user studies, evaluating success rate of corrections, dialogue efficiency, and user satisfaction. Expected outcomes include 40%+ reduction in iterations needed to achieve desired designs and a reusable framework applicable to other generative design tasks. This research advances personalizable, correctable ML models while providing practical tools for the HCI community.