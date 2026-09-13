---
source_paper: "arxiv_2303_07476.md"
generated_at: "2026-07-11T09:41:12.678411"
model: "openai/gpt-5.2"
summary_chars: 13025
---

# Challenges and Practices of Deep Learning Model Reengineering: A Case Study on Computer Vision

## Key Metadata
- **Authors:** Wenxin Jiang et al.
- **Year:** 2023 (arXiv:2303.07476)
- **Venue:** arXiv (manuscript appears targeted to *Empirical Software Engineering (EMSE)* based on artifact naming)
- **Core Contribution:** Mixed-methods, “process-view” empirical characterization of deep learning (DL) *model reengineering* via 348 GitHub defects (27 CV repositories) + practitioner/team-leader interviews, culminating in a defect taxonomy, challenge/practice themes, and a proposed reengineering workflow.

## Section Summaries

### Abstract
Context: Many engineering organizations are reimplementing and ex-
tending deep neural networks from the research community. We describe this pro-
cess as deep learning model reengineering.  
Problem statement: Deep learning model reengineering — reusing, reproducing,
adapting, and enhancing state-of-the-art deep learning approaches — is challeng-
ing for reasons including under-documented reference models, changing require-
ments, and the cost of implementation and testing. In addition, individual engi-
neers may lack expertise in software engineering, yet teams must apply knowledge
of software engineering and deep learning to succeed.  
Related works: Prior work has characterized the challenges of deep learning model
development, but as yet we know little about the deep learning model reengineering
process and its common challenges. Prior work has examined on DL systems from  
a “product” view, examining defects from projects regardless of the engineers’
purpose. Our study is focused on reengineering activities from a “process” view,
and focuses on engineers specifically engaged in the reengineering process.  
Methodology: Our goal is to understand the characteristics and challenges of deep
learning model reengineering. We conducted a case study of this phenomenon,
focusing on the context of computer vision. Our results draw from two data sources:
defects reported in open-source reeengineering projects, and interviews conducted
with open-source project contributors and the leaders of a reengineering team. In
the open-source data, we analyzed 348 defects from 27 open-source deep learning
projects. Meanwhile, our reengineering team replicated 7 deep learning models
over two years; we interviewed 2 practitioners and 6 reengineering team leaders to
understand their experiences.  
Results: Our results describe how deep learning-based computer vision techniques
are reengineered, analyze the distribution of defects in this process, and discuss
challenges and practices. We found that most defects (58%) are reported by re-
users, and that reproducibility-related defects tend to be discovered during training
(68% of them are). Our analysis shows that most environment defects (88%) are in-
terface defects, and most of environment defects (46%) are caused by API defects.
We also found that training defects have diverse symptomss and root causes. We
identified four main challenges in the DL reengineering process: model operational-
ization, performance debugging, portability of DL operations, and customized data
pipeline. Integrating our quantitative and qualitative data, we propose a novel
reengineering workflow.  
Future directions: Our findings inform several future directions, including: measur-
ing additional unknown aspects of model reengineering; standardizing engineering
practices to facilitate reengineering; and developing tools to support model reengi-
neering and model reuse.

### Introduction & Motivation
The paper studies *deep learning model reengineering*, defined as **reusing, replicating, adapting, or enhancing** an existing DL model to make research prototypes work in new environments, datasets, and product constraints—especially common in computer vision (CV). Prior empirical work largely takes a **“product view”** (defects regardless of engineer intent) and thus under-explains *how* defects arise during reengineering activities. Reengineering is hard due to under-documented reference implementations, fast-evolving frameworks/hardware, and high training/evaluation cost; additionally, DL debugging is intrinsically difficult (e.g., low interpretability). The authors aim to characterize defect manifestation/types/symptoms/root causes (RQ1–RQ4) and identify reengineering challenges and practices (RQ5), then synthesize these into a proposed workflow.

### Methodology
This is an **empirical mixed-methods case study** of *CV model reengineering* (not a new DL architecture). The study combines: (i) **failure analysis** of GitHub issues (RQ1–RQ4) and (ii) **interviews + an internal reengineering effort** (RQ5) to capture “process-view” practices and pain points.

**Failure analysis (GitHub defects):**
1. **Scope selection (CV):** chosen for prevalence in DL engineering and comparability with prior DL-SE studies.
2. **Repository selection:** start from popular CV architectures (e.g., YOLO, Mask R-CNN, Faster R-CNN, RetinaNet, Pix2pix, CenterNet) and use criteria **≥1K GitHub stars** and **≥50 closed issues**; search GitHub for implementations; limit to **≤5 repos per architecture** to reduce over-representation. Include both **solo** (single-model) and **zoo** (multi-model) repos (e.g., TensorFlow Model Garden).
3. **Issue selection filters:** (a) **closed** issues with an associated fix (to infer causes/fix discussion), (b) **≥10 comments** (sufficient detail). Typical sampling: top **20 most-commented** qualifying issues per repo; for very large framework zoos (e.g., `tensorflow/models`, `pytorch/vision`) randomly sample **10%** qualifying issues because highly-commented issues skew toward API requests rather than reengineering defects.
4. **Reengineering-defect identification:** manually exclude development Q&A and feature requests; include only defects arising during **reuse/replication/adaptation/enhancement**. From **427** sampled issues, **93** were filtered as non-defects, leaving **334** issues with reengineering defects, totaling **348** defects analyzed.

**Conceptual coding/taxonomies introduced for reengineering:**
- **Reporter types (Table 1):** *Re-user* (same code+data), *Adaptor* (new dataset/task), *Enhancer* (adds features, e.g., layers, hyperparameters, multi-GPU), *Replicator* (same algorithm/data/config but distinct implementation, e.g., TF vs PyTorch).
- **Defect manifestations (Table 2):**
  - *Basic defects:* code fails/runs incorrectly/OOM.
  - *Reproducibility defects:* runs but misses documented performance on same data (accuracy/latency).
  - *Evolutionary defects:* after changes to code/data, runs but misses desired/spec performance.
- **Stage-aware analysis:** defects are analyzed by DL lifecycle stages (environment setup, data pipeline, modeling, training & evaluation), and by symptoms/root causes.

**Qualitative component (RQ5):**
- Interviews with **2 open-source contributors**, **4 industry practitioners** (also summarized elsewhere as “2 practitioners”), and **6 student reengineering team leaders**; plus a **two-year** student-team effort replicating **7 DL models**. Data is analyzed to extract challenges/practices and to validate/supplement defect-study findings (including “member checking” with team leaders).

### Experiments & Results
Because this is an empirical software engineering paper, the “experiments” are **defect sampling, coding, and quantitative summarization**, not model training benchmarks. The principal dataset is **348 reengineering defects** from **27 GitHub repositories** (mix of research prototypes, replications, and widely reused zoos), sampled from **closed, discussion-rich issues (≥10 comments)**. Additionally, the authors incorporate qualitative observations from replicating **7 models over 2 years** plus interviews (2 OSS contributors + 4 industry practitioners + 6 student-team leaders).

**Evaluation outputs / “metrics”:** defect **frequencies and proportions** by (i) reporter type, (ii) manifestation type (basic/reproducibility/evolutionary), and (iii) DL stage + symptom/root cause categories. No BLEU/accuracy benchmarking is the focus; performance enters as *reproducibility/performance defects* (failure-to-match claimed accuracy/latency).

**Headline quantitative findings (from Abstract + main text):**
- **Who reports defects:** **58%** of defects are reported by **re-users** (downstream users attempting direct reuse).
- **Where reproducibility defects surface:** **68%** of **reproducibility-related defects** are discovered during **training**.
- **Environment defects:** **88%** of environment defects are **interface defects**; **46%** of environment defects are caused by **API defects** (e.g., framework/library version drift).
- **Training defects:** observed to have **diverse symptoms and root causes** (harder to categorize uniformly than environment or modeling issues).
- The paper also reports stage-skewed defect patterns: environment configuration dominated by API/interface issues; data pipeline + modeling dominated by assignment/initialization errors; training includes many performance/debugging failures and is reportedly hardest (especially performance defects).

**Compact results table (key reported proportions):**

| Finding | Reported number |
|---|---:|
| Total analyzed defects | 348 |
| Total repos | 27 |
| Defects reported by re-users | 58% |
| Reproducibility defects discovered during training | 68% |
| Environment defects that are interface defects | 88% |
| Environment defects caused by API defects | 46% |

**Baselines / comparisons:** rather than direct numeric baselines, the paper positions itself against prior DL defect studies (e.g., Islam et al. 2019; Humbatova et al. 2020; Sun et al. 2017; Zhang et al. 2018) by arguing those works largely take a “product view” and do not isolate *reengineering activity*. The authors also explicitly compare conceptual overlaps/differences to traditional software reengineering and to pre-trained model reuse.

**Ablation-style insights (component contribution):** not a model ablation, but the authors attribute observed reengineering difficulty to four recurring challenge clusters (below) and argue their workflow synthesizes where practices/tools could reduce defect incidence (especially earlier-stage detection for training/performance issues).

**Statistical significance / CI:** not reported in the provided excerpt (results are largely descriptive counts/percentages).

**Computational cost:** no aggregate GPU-hours are reported; cost is discussed qualitatively (training/evaluation expense and slowdowns on different hardware).

### Discussion & Conclusion
The paper reframes DL engineering evidence around a **distinct reengineering activity**, showing defect distributions differ by lifecycle stage and are heavily influenced by portability (APIs, environments, hardware). Key limitations include scoping to **computer vision**, reliance on **closed GitHub issues with ≥10 comments**, and manual coding (mitigated via calibration and agreement checks on samples). The authors propose future work in DL testing (stage-specific, end-to-end and differential testing), model reuse/portability tooling (e.g., better conversion + standardized artifacts), and standardized reengineering practices; they also note that foundation-model reengineering (LLMs, etc.) is not captured because data collection occurred in **2021**.

## Key Contributions
- Introduces and operationalizes **DL model reengineering** as a distinct engineering process (*reuse/replicate/adapt/enhance*), motivating a **process-view** lens rather than a product-only lens.
- Provides a **mixed-methods empirical dataset and analysis**: **348 reengineering defects** from **27** popular CV repositories plus interviews and a two-year, 7-model replication effort, yielding defect distributions across reporter types, manifestations, and DL stages.
- Identifies four recurring, high-level reengineering challenge areas—**model operationalization**, **performance debugging**, **portability of DL operations**, and **customized data pipelines**—and synthesizes them into a proposed **reengineering workflow** annotated with practices and defect hotspots.

## Potential Relevance
For hypothesis development on *reproducibility/portability/tooling in ML systems*, this paper provides concrete, stage-specific signals about where reengineering fails (e.g., API/interface dominance in environment setup; training-stage dominance for reproducibility defects). Its reporter/manifestation typology (re-user/adaptor/enhancer/replicator; basic/reproducibility/evolutionary) is directly reusable as an ontology for designing new measurements, benchmarks, or automated triage/testing tools. The “process-view” sampling argument also suggests a methodological hypothesis: **defect taxonomies and priorities may change materially depending on whether data is sampled by engineer intent/activity vs by artifact keywords alone**.