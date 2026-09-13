# Title
**Temporal Dataset Cards: Version-Aware Documentation for Evolving ML Datasets**

## Motivation
Current dataset documentation practices treat datasets as static artifacts, yet many widely-used ML datasets undergo continuous updates, corrections, and modifications. This creates reproducibility crises when researchers cite datasets without version tracking, leading to inconsistent results and evaluation ambiguity. Furthermore, deprecation decisions and quality issues discovered post-publication often go undocumented in earlier versions, perpetuating the use of problematic data. We need a systematic approach to track dataset evolution and propagate critical updates across versions.

## Main Idea
We propose **Temporal Dataset Cards**—a version-aware documentation framework that extends existing dataset cards with:

1. **Temporal Metadata Layer**: Structured changelog tracking additions, deletions, and corrections with timestamps and semantic versioning
2. **Retrospective Annotations**: Mechanism to backpropagate warnings (e.g., bias discoveries, consent issues) to all affected versions
3. **Impact Tracing**: Automated tools to identify papers/models using specific dataset versions and quantify result variance across versions
4. **Repository Integration**: APIs for HuggingFace, OpenML, and UCI to enforce version pinning in citations and enable temporal queries

Expected outcomes include improved reproducibility through precise version tracking, faster propagation of quality issues, and data repository features supporting dataset lifecycle management. This addresses multiple workshop themes: documentation, deprecation procedures, reproducibility, and repository design challenges.