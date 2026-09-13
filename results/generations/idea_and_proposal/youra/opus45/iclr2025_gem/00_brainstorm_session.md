# Research Brainstorm Session Results

**Session Date:** 2026-02-05
**Facilitator:** Research Question Architect
**Participant:** Pray

---

## Executive Summary

**Initial Interest:** Generative machine learning for biomolecular design - bridging the gap between computational ML research and experimental biology to create impactful real-world applications in protein, molecule, and nucleic acid engineering.

**Session Approach:** Auto-Fill Mode (Structured Input - Workshop CFP Detected)

**Session Duration:** < 1 minute (automated extraction from ICLR 2025 GEM Workshop CFP)

---

## Starting Context

**Background:** The GEM (Generative and Experimental perspectives in bioMolecular design) workshop addresses a critical disconnect between machine learning research and experimental biology. While generative ML shows significant potential for biomolecular design, many research efforts prioritize static benchmark performance over impactful real-world applications. The workshop aims to bring computationalists and experimentalists together to explore the strengths and challenges of generative ML in biology.

**Source Type:** Workshop CFP (ICLR 2025 GEM Workshop)

**Key Workshop Features:**
- Collaboration with Nature Biotechnology for exceptional submissions
- Two tracks: ML track (in-silico) and Biology track (wet lab results)
- Focus on bridging computational and experimental perspectives

---

## Session Plan

**Mode:** Auto-Fill (Structured Workshop CFP Input)
**Technique:** Direct extraction and synthesis from workshop scope and topics

---

## Technique Sessions

### Auto-Fill Extraction Process

**Input Analysis:**
The workshop CFP provides a well-defined research scope with two distinct tracks:

1. **ML Track Topics Identified:**
   - Generative ML advancements for biomolecular design with in silico results
   - Inverse design of all biomolecules
   - Modelling biomolecular data
   - Model interpretability

2. **Biology Track Topics Identified:**
   - Biological problems apt for ML applications
   - High-throughput data generation methods
   - Adaptive experimental design
   - Benchmarks, datasets, and oracles

**Synthesis Approach:**
Combined ML and Biology perspectives to formulate research questions that bridge both domains - the core mission of the workshop.

---

## Research Question Development

### Initial Question

How can generative machine learning methods be designed and validated to create impactful, experimentally-verifiable biomolecular designs that bridge the gap between computational benchmarks and real-world biological applications?

### Refined Question

How can we develop generative ML architectures for biomolecular design that (1) incorporate experimental feedback loops for iterative refinement, (2) produce designs that are practically synthesizable and testable in wet lab conditions, and (3) establish evaluation protocols that predict real-world performance beyond in-silico metrics?

### Detailed Sub-Questions

1. **Inverse Design Methodology:** What generative ML architectures (diffusion models, flow matching, VAEs, autoregressive models) are most effective for inverse design of proteins, small molecules, and nucleic acids, and how can their outputs be made experimentally tractable?

2. **Experimental Integration:** How can adaptive experimental design and high-throughput screening data be integrated into ML training loops to create closed-loop biomolecular design systems?

3. **Evaluation Gap:** What evaluation frameworks can bridge the gap between in-silico benchmark performance and wet-lab experimental success rates for ML-generated biomolecular designs?

4. **Interpretability for Biology:** How can model interpretability techniques be leveraged to provide biological insights that inform experimental validation strategies and increase trust in ML-generated designs?

5. **Benchmark Development:** What benchmark datasets, oracles, and evaluation protocols are needed to fairly assess generative models' ability to produce experimentally-valid biomolecular designs?

---

## Reference Papers

*Not provided in workshop CFP - will discover key papers in Phase 1*

**Suggested Search Directions for Phase 1:**
- Recent protein design papers using diffusion models (e.g., RFDiffusion, ProteinMPNN)
- Small molecule generation with experimental validation
- Adaptive experimental design / Bayesian optimization for molecules
- ML-guided directed evolution studies
- High-throughput screening data integration with ML

---

## Validation Results

### So What Test

**Significance:** This research addresses a fundamental bottleneck in applying ML to biology. Despite impressive benchmark results, many ML-generated biomolecular designs fail in wet lab validation. Solving this problem could:

1. **Accelerate drug discovery** by producing more experimentally-tractable candidate molecules
2. **Reduce costs** by improving the hit rate of ML-generated designs in expensive wet lab experiments
3. **Enable new therapeutics** through better protein and nucleic acid engineering
4. **Advance scientific understanding** by creating feedback loops between computation and experiment

The GEM workshop's collaboration with Nature Biotechnology underscores the field's recognition that this is a critical gap requiring urgent attention.

### Feasibility Check

**Assessment:** This research direction is highly feasible given:

1. **Data Availability:** High-throughput experimental data is increasingly available (protein fitness landscapes, molecular property assays, CRISPR screens)
2. **Methods Maturity:** Generative models for molecules (diffusion, flow matching) have reached a level where experimental validation is the natural next step
3. **Community Interest:** The workshop's two-track structure explicitly encourages ML + experimental collaboration
4. **Clear Scope:** Sub-questions can be addressed independently, allowing incremental progress

**Potential Challenges:**
- Access to wet lab validation (may require collaboration)
- Computational cost of training large generative models
- Domain expertise spanning both ML and biology

---

## Phase 1 Input Package

<phase1-input>

### research_question
How can we develop generative ML architectures for biomolecular design that (1) incorporate experimental feedback loops for iterative refinement, (2) produce designs that are practically synthesizable and testable in wet lab conditions, and (3) establish evaluation protocols that predict real-world performance beyond in-silico metrics?

### detailed_question
1. What generative ML architectures (diffusion models, flow matching, VAEs, autoregressive models) are most effective for inverse design of proteins, small molecules, and nucleic acids, and how can their outputs be made experimentally tractable?
2. How can adaptive experimental design and high-throughput screening data be integrated into ML training loops to create closed-loop biomolecular design systems?
3. What evaluation frameworks can bridge the gap between in-silico benchmark performance and wet-lab experimental success rates for ML-generated biomolecular designs?
4. How can model interpretability techniques be leveraged to provide biological insights that inform experimental validation strategies and increase trust in ML-generated designs?
5. What benchmark datasets, oracles, and evaluation protocols are needed to fairly assess generative models' ability to produce experimentally-valid biomolecular designs?

### reference_papers
*Not provided - will discover in Phase 1*

Suggested search areas:
- Protein diffusion models (RFDiffusion, Chroma, ProteinMPNN)
- Molecular generative models with experimental validation
- Bayesian optimization for molecular design
- High-throughput screening + ML integration
- Adaptive experimental design methods

</phase1-input>

---

## Session Insights

### Key Discoveries

- The GEM workshop explicitly identifies the ML-experiment gap as the central challenge, making this a timely and high-impact research direction
- Two-track structure (ML + Biology) suggests research should span both computational and experimental perspectives
- Nature Biotechnology collaboration indicates potential for high-impact publication if research successfully bridges both domains
- Focus areas (inverse design, interpretability, adaptive design, benchmarks) provide natural research pillars

### Techniques Used

- Auto-Fill Mode (structured input extraction)
- Workshop CFP analysis and topic synthesis
- Cross-domain gap identification (ML vs. experimental biology)

### Areas for Further Exploration

- Specific biomolecule types to focus on (proteins vs. small molecules vs. nucleic acids)
- Particular disease areas or applications (drug discovery, enzyme engineering, antibody design)
- Specific generative architecture comparisons (diffusion vs. flow matching vs. language models)
- Collaboration opportunities with experimental groups
- Computational resource requirements for different approaches

---

## Next Steps

**Immediate Action: Proceed to Phase 1 - Targeted Research**

The structured workshop CFP has been processed into a clear research direction. Phase 1 should:

1. **Literature Search:** Identify key papers on generative models for biomolecular design with experimental validation
2. **Gap Analysis:** Map which sub-questions have existing work vs. open problems
3. **Method Survey:** Catalog current approaches for each topic area
4. **Benchmark Review:** Identify existing evaluation frameworks and their limitations

**Command:** `/phase1-targeted`

---

*Session facilitated by YouRA Research Question Architect*
*Mode: Auto-Fill (Structured Workshop CFP Input)*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
