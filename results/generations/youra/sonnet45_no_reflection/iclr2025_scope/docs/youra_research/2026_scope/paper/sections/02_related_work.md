# Related Work

Our work addresses computational feasibility validation in research workflows—a process-level concern distinct from algorithmic optimization methods. We position our contribution against three related areas: model efficiency techniques, workflow tools, and negative results reporting.

## Model Compression and Optimization

The standard approach to large model constraints is reactive optimization: discover the model doesn't fit, then apply techniques to make it fit. Quantization methods reduce memory through lower precision (INT8, FP8, INT4) [Dettmers et al. 2022, 2023], achieving up to 75% memory reduction with minimal accuracy loss. Gradient checkpointing trades computation for memory by recomputing activations during backward pass [Chen et al. 2016]. Model parallelism frameworks like DeepSpeed [Rasley et al. 2020], Megatron-LM [Shoeybi et al. 2019], and FSDP [Zhao et al. 2023] distribute models across multiple GPUs, enabling training at scales beyond single-device capacity.

**Limitation:** These methods solve "how to make it fit" after discovering it doesn't. They require implementation effort to integrate (quantization-aware training modifications, parallelism strategy design, memory profiling) and assume the configuration is salvageable with optimization. Our work addresses the earlier question: "validate feasibility before implementing."

**Our Position:** We propose preventing the problem through early feasibility checking rather than solving it through post-hoc optimization. A lightweight memory estimation gate (~5 minutes) identifies infeasible configurations before weeks of implementation effort, with the option to either reformulate to practical scales or explicitly justify expensive optimization requirements.

## Distributed Training and Infrastructure

Production ML infrastructure addresses resource management through sophisticated scheduling and allocation. Ray [Moritz et al. 2018] and Kubernetes-based systems enable dynamic resource allocation. vLLM [Kwon et al. 2023] optimizes inference serving through paged attention and continuous batching. TorchX and similar orchestration tools manage multi-node training jobs.

**Limitation:** These systems assume infrastructure already exists and focus on efficient utilization. They optimize scheduling and throughput for *runnable* configurations, but don't validate whether a proposed experiment design is runnable given available resources. The validation gap exists before infrastructure deployment.

**Our Position:** Feasibility validation is orthogonal to infrastructure efficiency. Even with world-class infrastructure, researchers need early checks to avoid designing experiments that exceed available capacity. Our proposed gate integrates into research workflows (Phase 2C.5) before infrastructure allocation decisions.

## Workflow and Pipeline Tools

ML experiment tracking and management tools have matured significantly. MLflow [Zaharia et al. 2018], Weights & Biases [Biewald 2020], and DVC [Dmitry et al. 2020] handle versioning, reproducibility, and lineage tracking. Airflow and Kubeflow orchestrate complex pipelines. Recent research pipeline frameworks like Covalent and Metaflow manage workflow dependencies.

**Limitation:** Existing tools focus on orchestration (workflow execution), reproducibility (experiment tracking), and collaboration (artifact sharing). Resource validation is limited to runtime monitoring (job fails when OOM occurs) rather than proactive design-time checking. They track *what* ran, not *whether* proposed experiments can run.

**Our Position:** We identify missing proactive validation before execution begins. Our Phase 2C.5 gate complements existing tools by adding an early checkpoint: "Will this design fit available hardware?" This prevents workflow orchestration systems from attempting to execute infeasible configurations.

## Negative Results and Failure Analysis in ML

The ML community has growing recognition of negative results' value. NeurIPS and ICML introduced negative results tracks. Workshops like "Debugging Machine Learning Models" focus on failure modes. Papers document hypothesis refutations [Lipton & Steinhardt 2018], unexpected findings [Bender et al. 2021], and reproducibility challenges [Pineau et al. 2021].

**Limitation:** Negative results typically report *scientific* findings (hypothesis refuted, unexpected behavior, method doesn't generalize) or *implementation* challenges (bugs, numerical instability). Computational infeasibility failures are rarely documented because they feel like project management failures rather than research contributions. The workflow gap remains implicit.

**Our Position:** We frame computational infeasibility as a systematic workflow gap requiring process intervention, not merely bad resource planning. By analyzing *why* the failure occurred (missing feasibility checkpoint) rather than just *what* failed (Mixtral-8x7B too large), we elevate this from a project post-mortem to a meta-contribution about research process improvement.

## Positioning Summary

Our contribution is process-level, not algorithmic. Where prior work provides tools to *make* large models run (compression, parallelism), manage *running* experiments (workflow tools), or document *scientific* failures (negative results), we identify and address a missing validation checkpoint that prevents wasted implementation effort on infeasible designs. The feasibility gate sits between experiment design and implementation, catching resource constraint violations before coding begins—complementing reactive optimization with proactive validation.
