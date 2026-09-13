## Related Work

**Related Papers**

1. **Title**: π-Attention: Periodic Sparse Transformers for Efficient Long-Context Modeling (2025)
   - **Authors**: Dong Liu, Yanxuan Yu
   - **Summary**: Factorized attention into ring-local neighborhoods + deterministic π-stride skips; achieves O(kL + π log L) complexity; 8.3% lower perplexity than RingAttention with 50% fewer GPUs. Validates that structured sparsity works for long contexts using fixed periodic patterns.
   - **Year**: 2025

2. **Title**: Sparser is Faster and Less is More: Efficient Sparse Attention for Long-Range Transformers (2024)
   - **Authors**: Chao Lou, Zixia Jia, Zilong Zheng, Kewei Tu
   - **Summary**: SPARSEK Attention with scoring network and differentiable top-k mask operator; enables gradient-based sparse attention learning; linear time complexity and constant memory during generation. Demonstrates feasibility of gradient-based sparse attention learning.
   - **Year**: 2024

3. **Title**: Hardware-aligned Hierarchical Sparse Attention for Efficient Long-term Memory Access (2025)
   - **Authors**: Xiang Hu, Jiaqi Leng, Jun Zhao, et al.
   - **Summary**: Hardware-aligned hierarchical sparse attention (HSA) with RAMba achieving perfect passkey retrieval across 64M contexts; nearly constant memory footprint; hardware-specific kernel design. Proves hierarchical sparse attention scales to extreme contexts with fixed hardware-optimized patterns.
   - **Year**: 2025

4. **Title**: GENERator: A Long-Context Generative Genomic Foundation Model (2025)
   - **Authors**: Wei Wu, Qiuyi Li, Yuanyuan Zhang, et al.
   - **Summary**: Long-context generative genomics foundation model (98K bp context); pre-trained on 386B nucleotides; zero-shot variant effect prediction + prompt-guided cis-regulatory element design; competitive performance with improved efficiency. Uses manually designed fixed attention architecture.
   - **Year**: 2025

5. **Title**: Sparse-vDiT: Sparse Attention for Video Diffusion Transformers (2025)
   - **Authors**: Peyton Chen
   - **Summary**: Domain-specific sparse attention patterns for video diffusion; hand-designed sparsity exploiting temporal structure in video frames; accelerates video generation. Validates that domain-specific patterns outperform generic patterns.
   - **Year**: 2025

6. **Title**: DARTS: Differentiable Architecture Search (2019)
   - **Authors**: Hanxiao Liu, Karen Simonyan, Yiming Yang
   - **Summary**: Continuous relaxation of discrete architecture choices via softmax-weighted combination; bilevel optimization over architecture parameters α and model weights θ; gradient-based architecture search. Provides foundational method for differentiable neural architecture search.
   - **Year**: 2019

7. **Title**: MAML: Model-Agnostic Meta-Learning
   - **Authors**: Not specified
   - **Summary**: Bilevel optimization for meta-learning with inner loop for task-specific adaptation and outer loop for meta-parameter update; enables rapid adaptation to new tasks with few examples. Originally considered for HP-Genome but removed to eliminate hyperparameter complexity.
   - **Year**: Not specified

8. **Title**: Basenji: Sequential regulatory activity prediction across chromosomes with convolutional neural networks (2018)
   - **Authors**: David R. Kelley, et al.
   - **Summary**: CNN for predicting regulatory activity from DNA sequences; interpretability via visualization of learned convolutional filters; filters align with known transcription factor binding motifs. Demonstrates biological interpretability validation methodology.
   - **Year**: 2018

9. **Title**: ENCODE Project Database
   - **Authors**: Not specified
   - **Summary**: Encyclopedia of DNA Elements; comprehensive annotations of regulatory elements (promoters, enhancers, transcription factor binding sites, chromatin accessibility). Provides gold-standard genomics annotations used as training data and interpretability ground truth.
   - **Year**: Not specified

10. **Title**: JASPAR Transcription Factor Binding Motif Database
   - **Authors**: Not specified
   - **Summary**: Curated database of transcription factor DNA-binding motifs; position weight matrices (PWMs) for known regulatory motifs. Used for interpretability validation by comparing learned attention patterns to known biological motifs.
   - **Year**: Not specified

11. **Title**: Hierarchical Temporal Memory: Concepts, Theory, and Terminology (Numenta)
   - **Authors**: Not specified
   - **Summary**: Neuroscience-based cortical learning theory featuring multi-level pattern recognition (V1 edges → IT objects), sparse distributed representations (~2% active neurons), and temporal sequence learning. Provides architectural inspiration for hierarchical multi-scale attention design with biological plausibility.
   - **Year**: Not specified

**Key Challenges**

1. **Manual Attention Pattern Engineering**: Designing effective attention patterns for genomics requires both domain expertise in bioinformatics and deep learning, creating a significant engineering overhead and development time (months of manual iteration).

2. **Fixed vs. Adaptive Patterns**: Existing sparse attention approaches use either fixed periodic patterns (π-Attention) or hardware-optimized patterns (HSA) that cannot adapt to domain-specific structures, potentially missing optimal patterns for genomic data.

3. **Performance-Efficiency Trade-off**: Dense attention achieves best performance but has O(N²) complexity, while manual sparse patterns reduce computation but may sacrifice performance; finding optimal balance is challenging.

4. **Biological Interpretability Gap**: Black-box attention patterns lack scientific interpretability, making it difficult for biologists to trust and understand what learned models are capturing from genomic sequences.

5. **Hyperparameter Complexity**: Meta-learning and cross-domain approaches introduce excessive hyperparameters (8+ parameters including meta-learning rates, domain weights, bilevel optimization settings), creating "Hyperparameter Hell" that impedes practical feasibility.

6. **Scale Mismatch**: Genomic sequences have hierarchical structure at multiple scales (local regulatory elements at 200-500bp, global chromosome interactions at 1Mbp), but single-scale attention cannot capture both effectively.

7. **Gradient Signal Informativeness**: Uncertainty whether task loss gradients from genomic sequence modeling contain sufficient information to guide attention pattern learning toward biologically meaningful structures rather than dataset artifacts.

8. **Annotation Reliability**: Biological annotations (ENCODE, JASPAR) may be incomplete or noisy, creating challenges for validating learned pattern interpretability with potential false negatives (missing novel regulatory elements) or false positives.

9. **Sparsity Collapse Risk**: Learned sparse attention patterns may collapse to near-dense attention (>25% density) during training, losing efficiency benefits and computational advantages.

10. **Cross-Domain Generalization**: Extending learned attention patterns from genomics to other biological sequences (protein, RNA) or other domains (text, code) requires additional mechanisms not yet validated, limiting applicability of the approach.
