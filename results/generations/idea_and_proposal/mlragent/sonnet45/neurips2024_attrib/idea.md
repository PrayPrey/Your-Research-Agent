# Title
**Causal Data Provenance Graphs for Tracing Emergent Capabilities in Large Language Models**

## Motivation
Current data attribution methods treat training examples as independent contributors to model behavior, failing to capture how data interdependencies and compositional effects drive emergent capabilities. As models scale, we lack principled frameworks to answer: "Which combinations of training data sources caused this specific capability?" This limits our ability to debug failures, ensure compliance, and deliberately engineer desired behaviors through data curation.

## Main Idea
Construct **causal provenance graphs** that represent training data as nodes with edges encoding semantic and temporal dependencies (e.g., Wikipedia articles citing sources, code repositories with dependencies). During training, maintain lightweight "influence sketches" that track how data combinations—not just individual examples—contribute to capability emergence.

**Methodology:**
1. Build hierarchical data graphs clustering semantically related examples
2. Develop efficient influence tracking using gradient-based sketching over data subgraphs
3. Apply interventional analysis: systematically ablate data subgraphs and measure capability degradation
4. Validate on controlled settings where capabilities have known data requirements (e.g., multilingual reasoning requiring parallel corpora)

**Expected Outcomes:**
- Attribution maps showing which data source *combinations* drive specific capabilities
- Scalable algorithms operating on billion-scale datasets
- Practical tools for detecting contamination propagation and optimizing data mixtures

**Impact:** Enable targeted dataset debugging, contamination tracing through dependency chains, and principled data acquisition strategies for capability engineering.