# Title
BioConstruct-SC: A Psychometric Framework for Measuring Biological Representation Quality in Single-Cell Foundation Models

# Motivation
Single-cell foundation models (scGPT, Geneformer, UCE) promise to extract "meaningful representations" from biological data, yet the field lacks rigorous methods to measure what "meaningful" actually means. Current evaluation relies on task-specific metrics that cannot be compared across models or tasks, making it impossible to determine which models truly capture biological understanding versus those that merely memorize patterns. This gap prevents principled model selection and hinders progress toward universal biological simulators.

# Main Idea
We propose adapting psychometric measurement theory—specifically hierarchical Item Response Theory (IRT)—to evaluate biological foundation models. The core insight is that biological understanding can be decomposed into measurable latent constructs, analogous to how educational testing measures cognitive abilities.

Our four-step methodology: (1) Apply exploratory factor analysis to model-task performance matrices to identify 2-4 biological constructs; (2) Specify a bifactor IRT model capturing general and construct-specific abilities; (3) Estimate model ability parameters on common scales; (4) Validate using multi-source biological ground truth (ENCODE, Reactome, Perturb-seq).

The key prediction: models with high construct validity (convergent r>0.7, discriminant silhouette>0.3) will generalize better to held-out tasks than models with high raw performance but low validity. This framework enables fair cross-model comparison and operationalizes "meaningful representation" through empirical evidence requirements.