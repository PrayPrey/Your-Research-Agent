---
source_paper: "arxiv_2504_03887.md"
generated_at: "2026-07-10T05:21:22.734383"
model: "openai/gpt-5.2"
summary_chars: 15124
---

# VeritasEst: Accurate GPU Memory Prediction for Deep Learning Jobs through Dynamic Analysis

## Key Metadata
- **Authors:** Jiabo Shi et al.
- **Year:** 2025 (arXiv:2504.03887)
- **Venue:** arXiv
- **Core Contribution:** A **GPU-free**, **CPU-profiler-driven** dynamic analysis tool that predicts **peak GPU “segment” memory** for PyTorch training by reconstructing and simulating allocator-level memory sequences (CUDACachingAllocator/BFC).

## Section Summaries

### Abstract
> Abstract—The benefits of Deep Learning (DL) impose significant  
> pressure on GPU resources, particularly within GPU cluster, where  
> Out-Of-Memory (OOM) errors present a primary impediment  
> to model training and efficient resource utilization. Conventional  
> OOM estimation techniques, relying either on static graph analysis  
> or direct GPU memory profiling, suffer from inherent limitations:  
> static analysis often fails to capture model dynamics, whereas  
> GPU-based profiling intensifies contention for scarce GPU resources.  
> To overcome these constraints, VeritasEst emerges. It is an  
> innovative, entirely CPU-based analysis tool capable of accurately  
> predicting the peak GPU memory required for DL training  
> tasks without accessing the target GPU. This ”offline” prediction  
> capability is VeritasEst’s core advantage, allowing accurate memory  
> footprint information to be obtained before task scheduling, thereby  
> effectively preventing OOM and optimizing GPU allocation. Its  
> performance was validated through thousands of experimental runs  
> across convolutional neural network (CNN) models: compared to  
> baseline GPU memory estimators, VeritasEst significantly reduces  
> the relative error by 84%, lowers the estimation failure probability  
> by 73%. VeritasEst represents a key step towards efficient and  
> predictable DL training in resource-constrained environments.  

### Introduction & Motivation
GPU clusters frequently waste scarce GPU time on jobs that fail with out-of-memory (OOM); prior cluster measurements report **~9% of training tasks fail due to OOM**. Existing estimators either (i) rely on **static graph analysis** that misses training-time dynamics (e.g., `optimizer.zero_grad`, optimizer state allocation), or (ii) use **GPU-based profiling**, which itself consumes the scarce resource and increases scheduling contention. The authors aim to predict **minimum runnable GPU memory (peak usage)** *before scheduling*, without using a GPU at all. The key gap addressed is modeling **allocator-level GPU memory (“segments”)** and **dynamic allocation/free sequences** using only CPU-side traces.

### Methodology
VeritasEst is a **CPU-based GPU memory estimator** for **PyTorch training** that reconstructs a GPU-like memory allocation timeline from **PyTorch Profiler** traces, then **simulates CUDA’s caching allocator** to predict **peak segment memory** (true GPU-reserved memory), rather than naïvely summing tensor sizes. It is built on three observations: (1) **high-level call sequence** (Python→ATen dispatch) is consistent across CPU/GPU; (2) many PyTorch operators have **comparable memory behavior** across kernels; (3) given an ordered sequence of alloc/free requests, allocator behavior is predictable.

**Pipeline (Fig. 1)**:
1. **Data Analysis (Profiler parsing):** consumes JSON traces but uses only four event types:
   - `python function` → constructs a **layer call tree** (layer boundaries like `Conv2d`, `ReLU`, `VGG16`).
   - `cpu op` → operator metadata + **sequence number** (links forward/backward ops); organized via a **time-interval tree** idea to find relevant roots.
   - `user annotation` → identifies `profiler.step`, `optimizer.zero_grad`, `optimizer.step` to segment iterations and optimizer phases.
   - `cpu instant event` → raw memory alloc/free activities (addr, size, reserved/allocated).
   A core task is pairing alloc/free of reused addresses; they perform sequential binding via **Algorithm 1** to produce “memory blocks” with `(alloc_time, free_time, size)`; unfreed blocks become **permanent**.

2. **Data Link (timestamps-only correlation):** layers (python functions) are linked to `cpu op` within their start/end interval (wrapper layers excluded); forward ops pull in backward ops via **sequence numbers**. Operators are linked to memory blocks via overlapping timestamps. To reduce CPU/GPU mismatch due to CPU-specific temporaries, VeritasEst filters blocks **allocated and freed entirely within an operator’s execution window**, keeping primarily “retained-after-op” blocks (empirically closer to GPU behavior).

3. **Sequence Orchestration (GPU-like timing correction):** reshapes CPU-derived block lifetimes into GPU-realistic ones:
   - **Model transfer (`model.to(device)`)** isn’t in CPU traces; they approximate persistent model memory as **gradient-sized memory**, validated using PyTorch Snapshot Profiler with **0–1.2% error**, and fix allocation ordering to match backward-vs-load order.
   - **Batch data** blocks live for exactly one iteration; batch memory is obtained from the PyTorch dataloader; alloc/free span the iteration.
   - **Gradients**: CPU training often frees early, but on GPU, lifetime is controlled by `optimizer.zero_grad`; thus **all gradient blocks’ free_time is moved to the next `optimizer.zero_grad`** (or retained until it occurs).
   - **Optimizer state**: blocks created during `optimizer.step` are inspected; for optimizers like **Adam**, extra state tensors mirror parameter shapes. VeritasEst **excludes blocks whose sizes do not match any model parameter size** and marks optimizer-state-like blocks as **permanent until epoch end**.
   - **Repetitive iterations:** because non-SGD optimizers allocate additional permanent state early, VeritasEst generates sequences for **two iterations by default** (paper text mentions “xMen” here, but context indicates VeritasEst).

4. **Memory Allocation Simulation:** requests are rounded and packed into **segments** (allocator-reserved blocks) by a Python simulator of **CUDACachingAllocator** using **Best Fit with Coalescing (BFC)** [20]. The predicted peak is the maximum total segment size requested over the simulated trace.

**Algorithm 1 (as given, CPU instant event grouping):**
```text
Algorithm 1: cpu instant event Grouping

Data: cpu instant event Data
Result: Set of Time-based Memory Block
addr map ← {};
node map ← {};
data ← get sorted cpu event data();
foreach trace ∈ data do
  addr ← get addr(trace);
  if addr /∈ addr map then
    block ← create memory block(trace);
    addr map[addr] ← block;
  else
    addr map[addr].mark as free(trace);
    block ← addr map.pop(addr);
    node map[block.alloc time].append(block);
foreach remaining ∈ addr map do
  alloc time ← remaining.alloc time;
  node map[alloc time].append(remaining);
return sort by alloc time(node map);
```

**Key definitions (crucial novelty vs tensor-sum estimators):**
- **Tensor memory**: blocks used by parameters/activations/gradients, allocated *from* allocator-managed pools.
- **Segment memory**: blocks requested from GPU and cached by allocator; **GPU memory consumption = total segment memory**, not tensor totals.

**Equations used for OOM decision and error:**
\[
\hat{OOM}_{jde} =
\begin{cases}
1,& \hat{M}^{peak}_{jde} > M^{max}_d\\
0,& \hat{M}^{peak}_{jde} \le M^{max}_d
\end{cases}
\tag{1}
\]
\[
OOM_{jid} =
\begin{cases}
1,& True\\
0,& False
\end{cases}
\tag{2}
\]
\[
C_{jde1} =
\begin{cases}
1,& \hat{OOM}_{jde} = OOM_{jd1}\\
0,& \hat{OOM}_{jde} \ne OOM_{jd1}
\end{cases}
\tag{3}
\]
\[
C_{jde2} =
\begin{cases}
1,& C_{jde1}=1 \land OOM_{jd2}=0\\
1,& C_{jde1}=1 \land OOM_{jd1}=1\\
0,& \text{otherwise}
\end{cases}
\tag{4}
\]
\[
error_{jide} = \frac{\left\lVert \hat{M}^{peak}_{jde}-M^{peak}_{jid}\right\rVert}{M^{peak}_{jid}}
\tag{5}
\]
\[
P_{jie} = \frac{N-\sum_{n=1}^{N} C_{jide}}{N}
\tag{6}
\qquad
\tilde{error}_{jide} = \mathrm{median}(error_{jide})
\tag{7}
\]

### Experiments & Results
**Goal:** compare VeritasEst to three state-of-the-art estimators spanning **static analysis**, **learned prediction**, and **GPU-based measurement**, emphasizing both (i) **peak prediction accuracy** and (ii) **OOM-avoidance reliability** (failure probability), under controlled repeated runs.

**Baselines (as implemented/selected by authors):**
- **DNNMem** [11] (static graph + allocator simulation).
- **SchedTune** [12] (data-driven / pre-trained model; code available).
- **LLMem** [15] (direct GPU interaction).
(Horus [14] excluded as its focus is FLOPS utilization and simplistic memory estimation.)

**Hardware/software & controls:**
- Server: **24-core Intel i9**, **128GB RAM**.
- GPUs: **GeForce 4070Ti (12GB)** and **GeForce 4060 (8GB)**.
- Containerized environment: `pytorch:2.3.1-cuda12.1-cudnn8-devel`.
- Isolation: one container per run; one process fully occupies a GPU.
- To avoid extra caching variance: set **CUBLAS workspace size = 0** and **CUFFT plan size = 0** in PyTorch.
- Fixed initial GPU memory overhead \(M^{init}_d\): monitor (127MB on 4070Ti), terminal (112MB), plus ~15MB initial per GPU; accounted for in validation.

**Models/optimizers tested (Table I, 16 CNN-family models × 5 optimizers):**

| Model (16) | Source |
|---|---|
| VGG11, VGG16, VGG19 | [31] |
| ResNet50, ResNet101, ResNet152 | [22] |
| MobileNetV2 | [32] |
| MobileNetV3 (Small/Large) | [33] |
| MnasNet | [34] |
| RegNetX (400MF, 32GF) | [35] |
| RegNetY (400MF, 32GF) | [35] |
| ConvNeXt (Tiny, Base) | [36] |

Optimizers (5): **Adam, SGD, Adagrad, RMSprop, AdamW**.  
Input tensor shape fixed to **[3, 86, 86]**. Batch sizes varied.

**Evaluation protocol (two-step validation):**
1. **Initial validation:** each estimator predicts \(\hat{M}^{peak}_{jde}\), declares \(\hat{OOM}_{jde}\) via (1), then the job is run on the GPU to obtain actual \(OOM_{jd1}\) and actual peak \(M^{peak}_{jd1}\) via **NVML**; correctness \(C_{jde1}\) via (3); relative error via (5).
2. **Subsequent validation:** set allowed max runnable memory to \(M^{init}_d + \hat{M}^{peak}_{jde}\) (and check against \(M^{max}_d\)); rerun to observe \(OOM_{jd2}\) and \(M^{peak}_{jd2}\); correctness \(C_{jde2}\) via (4); error via (5).  
Each run is limited to **10 iterations** because peak stabilizes after a few iterations.

**ANOVA experiment (main large-scale study):**
- Configurations: **16 models × 5 optimizers × 16 batch sizes** (batch sizes **[10, 530] step 40**) = **1,120** configs.
- Repetitions: **3×** on **GeForce 4060**, totaling **3,360 runs** (only 38 failures).

**Key quantitative results (reported):**
- Overall across thousands of runs (paper summary claim): **median relative error = 5.46%**, **estimation failure probability = 13.59%**.
- Compared to baselines [11], [12], [15]: **relative error ↓ 84.32%**, **failure probability ↓ 73.44%**.

**Per-optimizer accuracy highlights (Initial validation error distributions):**
- **SGD:** VeritasEst error range **0.17%–32.56%**, overall median **6.68%**; best baseline DNNMem median **16.76%**; SchedTune max **387.44%**, LLMem max **306.69%**.
- **Adam:** VeritasEst overall median **5.93%**; DNNMem median **23.60%**; SchedTune max **278.48%**; LLMem max **110.03%**.

**Failure probability vs median error (quadrant analysis using (6)(7), threshold 20% for both axes):**
- VeritasEst points mostly in **optimal quadrant** (low failure, low median error) for both **SGD** and **Adam**, with few under/over-estimations.
- DNNMem shows **polarization**: some optimal, some **worst quadrant** with failure rate reaching **100%** in multiple cases (especially under Adam, consistent with static-analysis limitations for optimizer dynamics).
- SchedTune tends toward **overestimation quadrant** (lower failure but high error variability).
- LLMem remains generally **unsatisfactory** in this analysis.

**Runtime (average):**
- VeritasEst: **10.98 s** (elsewhere reported average ~**11.72 s**).
- DNNMem: **61.08 s** (slowest; heavy analysis).
- SchedTune: **1.55 s** (fastest; pretrained inference).
- LLMem: **5.40 s** (GPU-assisted collection).

**Compact results table (from reported aggregates):**

| Estimator | Median relative error (overall) | Failure probability (overall) | Avg runtime |
|---|---:|---:|---:|
| **VeritasEst** | **5.46%** | **13.59%** | ~11 s |
| DNNMem [11] | higher (e.g., 16.76% SGD; 23.60% Adam) | higher; sometimes 100% by model | 61.08 s |
| SchedTune [12] | highly variable (max 278–387%) | often low but overestimates | 1.55 s |
| LLMem [15] | variable (max 110–307%) | unsatisfactory overall | 5.40 s |

**Ablations:** no explicit ablation table is included in the provided text; however, the analysis attributes gains mainly to (i) correcting **gradient lifetime via `optimizer.zero_grad`**, (ii) modeling **segment memory** via allocator simulation, and (iii) sequence/timestamp-based **layer-op-block linking** plus filtering of CPU-only temporaries.

**Compute cost reporting:** they report wall-clock estimator runtime per run (seconds). GPU hours are not explicitly reported; runs are containerized and repeated; each run uses up to 10 iterations.

### Discussion & Conclusion
VeritasEst reframes GPU memory estimation as a **GPU-free** problem: predict GPU peak memory using only **CPU profiling traces** and **allocator-level simulation**, thereby avoiding cluster contention caused by GPU-based probing. The approach achieves **~5–6% median relative error** and materially reduces OOM prediction failures versus static, learned, or GPU-dependent baselines. Limitations/future work include addressing **underestimation due to GPU cache data**, improving performance, and extending to **distributed training** and **LLM fine-tuning** while remaining GPU-free.

## Key Contributions
- **GPU-free dynamic estimator:** Predicts **peak GPU segment memory** for PyTorch training without accessing the target GPU, enabling *offline* pre-scheduling OOM prevention.
- **Allocator- and sequence-aware modeling:** Reconstructs a **training-time memory activity sequence** (alloc/free lifetimes) from CPU profiler events, then simulates **CUDACachingAllocator (BFC)** to account for fragmentation/caching effects.
- **General memory trace generation from CPU profiles:** Produces a detailed **GPU-oriented memory change trace** by linking `python function` → `cpu op` → memory blocks using timestamps and correcting lifetimes for model/batch/gradients/optimizer states; released as open source (per paper claim).

## Potential Relevance
VeritasEst provides a concrete blueprint for **profiling-driven resource prediction**: turning low-level profiler events into allocator-accurate peak memory forecasts, which is directly useful for hypotheses on **scheduler-aware training**, **profiling minimality**, or **cross-device invariants (CPU→GPU)**. Its explicit handling of **segment-vs-tensor memory** and **optimizer/zero_grad-dependent lifetimes** offers reusable methodological components for extending to **distributed training** and **LLM fine-tuning** memory estimators, as well as for designing better **OOM-robust admission control** policies.