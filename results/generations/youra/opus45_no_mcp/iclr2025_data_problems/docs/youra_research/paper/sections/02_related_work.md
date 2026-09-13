# Related Work

## N-gram Overlap Detection

The dominant approach to contamination detection relies on exact substring matching. Brown et al. introduced 13-gram overlap in GPT-3, flagging training documents sharing 13+ consecutive tokens with benchmark items. OpenAI's GPT-4 technical report refined this to 50-character overlap thresholds. These methods scale efficiently via suffix arrays and Bloom filters, enabling analysis of trillion-token corpora.

However, n-gram methods fail completely on paraphrased contamination. Yang et al. demonstrate that training Llama-2-13B on rephrased MMLU achieves 85.9% accuracy while evading n-gram detection entirely. The fundamental limitation is definitional: exact matching cannot capture semantic equivalence across phrasings. Tools like overlapy and wellecks/overlap implement efficient n-gram analysis but inherit this vulnerability.

## Quiz-Based and Behavioral Methods

Golchin and Surdeanu's Data Contamination Quiz (DCQ) takes a behavioral approach: generate completion prompts from benchmark items and measure whether models reproduce memorized content with suspiciously high accuracy. DCQ achieves higher memorization detection rates than n-gram methods and works without training data access.

The limitation is scalability. DCQ provides binary output per item and requires individual probing, preventing benchmark-wide continuous scoring. ConStat extends behavioral detection through performance-based analysis but similarly lacks continuous metrics suitable for ranking contamination severity.

## Embedding and Density Approaches

Semantic similarity methods using embeddings represent a middle path: match semantically equivalent content regardless of surface form. However, density estimation fails in high-dimensional embedding spaces—a well-documented limitation in representation learning. Clustering-based approaches suffer similar curse-of-dimensionality problems.

## Surveys and Taxonomies

Recent surveys systematically categorize detection methods. The ACL 2024 survey by Yale NLP documents contamination levels up to 45% in popular LLMs across common benchmarks. A taxonomy from 2024 distinguishes dataset inspection, membership inference, and example generation approaches, noting that all existing methods have significant blind spots.

## Our Position

We address a gap in the detection landscape: no existing method provides scalable, continuous-valued, paraphrase-resistant contamination measurement. Our approach differs fundamentally from prior work:

- **vs. N-gram methods**: SSI targets behavioral consequences rather than surface overlap, potentially detecting paraphrased contamination.
- **vs. DCQ**: SSI provides a continuous metric from variance computation, enabling severity quantification rather than binary classification.
- **vs. Embedding density**: SSI uses variance (robust in high dimensions) rather than density estimation.

The key insight is measuring the *consequence* of diverse training exposure—confidence uniformity—rather than matching training content directly. We demonstrate this mechanism is valid while documenting that the specific SSI formulation fails as a practical detector.
