---
source_paper: "arxiv_2103_12028.md"
generated_at: "2026-07-30T06:11:30.320618"
model: "openai/gpt-5.2"
summary_chars: 11643
---

# Quality at a Glance: An Audit of Web-Crawled Multilingual Datasets

## Key Metadata
- **Authors:** Julia Kreutzer et al.
- **Year:** 2021 (arXiv:2103.12028; later revision acknowledges TACL review process)
- **Venue:** arXiv (paper text suggests journal-style review; likely later TACL)
- **Core Contribution:** A large-scale human audit (plus targeted automatic analyses) showing that many web-crawled “multilingual” corpora—especially low-resource ones—contain pervasive wrong-language, non-linguistic, misaligned, or mislabeled content, and proposing practical auditing/documentation recommendations.

## Section Summaries

### Abstract
With the success of large-scale pre-training
and multilingual modeling in Natural Lan-
guage Processing (NLP), recent years have
seen a proliferation of large, web-mined
text datasets covering hundreds of
lan-
guages. We manually audit
the quality
of 205 language-speciﬁc corpora released
with ﬁve major public datasets (CCAligned,
ParaCrawl, WikiMatrix, OSCAR, mC4).
Lower-resource corpora have systematic is-
sues: At least 15 corpora have no usable
text, and a signiﬁcant fraction contains less
than 50% sentences of acceptable quality. In
addition, many are mislabeled or use non-
standard/ambiguous language codes. We
demonstrate that these issues are easy to de-
tect even for non-proﬁcient speakers, and
supplement the human audit with automatic
analyses.
Finally, we recommend tech-
niques to evaluate and improve multilin-
gual corpora and discuss potential risks that
come with low-quality data releases.

### Introduction & Motivation
Web-mined corpora (often from Common Crawl) have become the default substrate for massively multilingual LMs and MT systems, yet their per-language quality—especially for low-resource languages—is rarely measured directly. Existing evaluations typically tune mining pipelines and report downstream gains on a small set of high-resource languages, which can mask severe failures on underrepresented languages. The paper addresses this gap by directly auditing sentence(-pair) quality across multiple widely used multilingual datasets and by analyzing language-code labeling issues that hinder reuse and transparency. The broader motivation is risk reduction: poor-quality corpora can silently degrade downstream systems, mislead the community about “coverage,” and amplify harm (e.g., offensive content, factual mistranslations).

### Methodology
The core method is a **manual sentence-level audit** of language-specific subsets from five public web-crawled datasets—**CCAligned, ParaCrawl v7.1, WikiMatrix, OSCAR, mC4**—paired with a lightweight **error taxonomy** and follow-up **automatic analyses** (LangID filtering and language-code audits). For each language within each dataset, the authors **randomly sample up to 100 lines** (lines may be words → paragraphs depending on segmentation). For **parallel corpora** (CCAligned, ParaCrawl, WikiMatrix), they focus on pairs with **English** (plus Spanish for some ParaCrawl pairs), and annotate sentence pairs; for **monolingual corpora** (OSCAR, mC4) they annotate sentences (mC4 is sentence-split and deduplicated before rating). **Participants:** 51 NLP-community volunteers covering ~70 languages with proficient skills; when no expert exists, annotators use “detective work” (dictionaries/web search) aiming for an *upper bound* on quality.

**Taxonomy (labels):** for parallel data: **C** (correct translation, any; with subtypes **CC** natural, **CB** boilerplate/low-quality, **CS** short), **X** (incorrect translation but both sides are in the correct languages), **WL** (wrong language on at least one side, but linguistic), **NL** (non-linguistic content on at least one side). For monolingual data: **C/WL/NL** only. Annotators additionally flag **offensive** and **pornographic** content. The authors aggregate label proportions per language and report **macro-averages** (equal weight per language) and **micro-averages** (weighted by each audited language’s sentence count in the dataset, emphasizing high-resource languages). They also evaluate whether **non-proficient** raters can approximate expert audits by computing directed agreement **Acc-n** at different label granularities (6-way, 4-way, 2-way).

Automatic follow-ups: (i) apply **CLD3** sentence-level LangID to CCAligned and measure precision against audit-derived expectations; (ii) train a **Transformer-based LangID** (in the spirit of Caswell et al., 2020) and measure precision/recall trade-offs when filtering; (iii) audit **language-code correctness** against **BCP-47/ISO639** conventions across datasets (plus JW300).

### Experiments & Results
**Audited scope / sampling:** They manually label samples for **205 language-specific corpora** (also described as 230 per-language subsets earlier), drawn from five datasets. Per-language sampling is **100 lines** (some languages have <100). Coverage and sampling fractions (Table 3) emphasize how tiny audited subsets are relative to total data:

- **CCAligned:** 65 / 119 languages audited (54.62%); 8037 / 907M sentences (0.00089%)
- **ParaCrawl v7.1:** 21 / 38 (55.26%); 2214 / 521M (0.00043%)
- **WikiMatrix:** 20 / 78 (25.64%); 1997 / 95M (0.00006%)
- **OSCAR:** 51 / 166 (30.72%); 3517 / 8.4B (0.00004%)
- **mC4:** 48 / 108 (44.44%); 5314 / 8.5B (0.00211%)

**Primary metrics:** percentage of samples labeled **C**, **X**, **WL**, **NL**, plus incidence of **offensive/porn**. They report both **macro** and **micro** averages to show how high-resource languages dominate micro statistics.

#### Main audit results (from Table 3)
| Dataset | Avg type | C | X | WL | NL | offensive | porn | #langs=0%C | #langs<50%C |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CCAligned | macro | 29.25% | 29.46% | 9.44% | 31.42% | 0.01% | 5.30% | 7 | 44 |
| CCAligned | micro | 53.52% | 32.25% | 3.60% | 10.53% | 0.00% | 2.86% | – | – |
| ParaCrawl v7.1 | macro | 76.14% | 19.17% | 3.43% | 1.13% | 0.00% | 0.63% | 0 | 4 |
| ParaCrawl v7.1 | micro | 83.00% | 15.27% | 1.04% | 0.69% | 0.00% | 0.33% | – | – |
| WikiMatrix | macro | 23.74% | 68.18% | 6.08% | 1.60% | 0.00% | 0.00% | 1 | 19 |
| WikiMatrix | micro | 50.58% | 47.10% | 1.35% | 0.94% | 0.00% | 0.00% | – | – |
| OSCAR | macro | 87.21% | – | 6.26% | 6.54% | 0.14% | 0.48% | 7 | 11 |
| OSCAR | micro | 98.72% | – | 0.52% | 0.75% | 0.18% | 1.63% | – | – |
| mC4 | macro | 72.40% | – | 15.98% | 11.40% | 0.06% | 0.36% | 0 | 9 |
| mC4 | micro | 92.66% | – | 2.33% | 5.01% | 0.03% | 0.08% | – | – |

**Key qualitative findings:**
- Severe issues concentrate in **low-resource** corpora: across all audited corpora, **87** had **<50% usable** data, and **15** had **0% in-language** content.
- **Parallel data**: **WikiMatrix** shows very high **X** (misalignment/mistranslation): macro-average **68.18% X**, consistent with Wikipedia’s “comparable not parallel” structure; CCAligned has high **NL** (31.42% macro) and notable pornographic content (macro **5.30%**, with **>10% porn** in CCAligned for **11 languages**).
- **Monolingual data**: **mC4** has the highest wrong-language ratio among monolingual sets (macro **15.98% WL**) and **11.40% NL**; **4/48** audited mC4 languages have **>50%** content in other languages.
- Confusions are often with **related high-resource languages** or **“out-of-model cousin”** errors where unsupported languages are mapped to a “similar” supported one (e.g., **Shona `sn`→Kinyarwanda `rw`**, **Hawaiian `haw`→Twi `tw/ak`**).

**Low-resource size–quality relationship:** Quality correlates positively with corpus size (Spearman) across datasets: **mC4 r=0.66**, **CCAligned r=0.53**, **WikiMatrix r=0.49**, **ParaCrawl r=0.43**, **OSCAR r=0.37**. However, some high-count languages still have extremely low quality (e.g., CCAligned **Javanese `en-jv_ID` 5% C**, **Tagalog `en-tl_XX` 13% C**).

**Non-expert audit reliability:** Directed agreement of non-proficient vs proficient annotators:
- **CCAligned subset:** mean **Acc-6=0.66**, **Acc-4=0.72**, **Acc-2=0.79** (binary C vs non-C is much easier).
- **OSCAR subset:** mean **Acc-6=0.98** (very high, reflecting simpler monolingual judgments and/or clearer cases).

**Automatic filtering experiments:**  
- **CLD3** sentence-level LangID on CCAligned yields only **40.6% average precision** against the audit-derived expectations (limited utility for robust filtering).
- A **Transformer-based LangID** filter improves **median precision** on noisy CCAligned corpora (<50% correct) from **13.8% → 43.9%**, but with **77.5% recall loss** (major data shrinkage). Example improvements: **Lingala precision 8%→80%**, **Oromo 2%→33%**, yet both lose ~50% of already-scarce correct sentences (e.g., Lingala 22k→3k; Oromo reduced to ~1k), undermining downstream usability.

**Downstream impact proxy (translation):** They correlate audit quality with **M2M-124** translation quality on **FloRes** for 21 overlapping languages:
- Data quality vs **spBLEU**: **Spearman ρ=0.44 (p=0.041)**  
- Data size vs **spBLEU**: **ρ=0.66 (p=0.00078)**
- Product of quality and size (expected good-sentence count) vs **spBLEU**: **ρ=0.73 (p=0.00013)**  
For English→X, trends persist (quality weaker; size/product stronger), e.g. product correlation **ρ=0.80 (p=0.0000087)**.

### Discussion & Conclusion
The audit shows that “multilingual coverage” in popular crawled datasets can be illusory: many low-resource corpora are dominated by wrong-language or non-linguistic content, and parallel corpora can contain large fractions of misleading near-parallel mismatches. Simple human checks (even by non-experts) can detect major failures quickly, but automated LangID filtering is not a universal fix due to harsh precision–recall trade-offs, especially when data is already scarce. The authors advocate routine per-language sampling audits, better documentation/quality scores, and stricter language-code standards (BCP-47) to reduce downstream harm and misinterpretation.

## Key Contributions
- **Large-scale manual quality audit** of **205** language-specific corpora across **CCAligned, ParaCrawl, WikiMatrix, OSCAR, mC4**, using a shared, lightweight error taxonomy (C/X/WL/NL + boilerplate/short + offensive/porn).
- **Quantitative evidence of systematic low-resource failures**: at least **15 corpora with 0% usable text**, many with **<50%** acceptable sentences; parallel corpora show high misalignment (e.g., **WikiMatrix 68.18% X** macro).
- **Actionable analysis beyond auditing**: (i) non-expert audit feasibility (e.g., **Acc-2 up to 0.79** on CCAligned), (ii) limitations of LangID filtering (**CLD3 precision 40.6%**; Transformer filter improves precision but loses **77.5% recall**), and (iii) identification of widespread **language-code mislabeling/nonstandard codes** (83 affected corpora across several datasets, plus extensive issues in JW300).

## Potential Relevance
For hypothesis development on multilingual pretraining/MT data quality, this paper provides a concrete **measurement protocol** (100-sentence per-language audit + macro/micro reporting) and an **error taxonomy** that can be reused to audit new crawls or model training mixtures. Its results motivate hypotheses about **why low-resource performance saturates** (effective good-data count ≈ *quality × size* correlates best with downstream BLEU) and caution that aggressive filtering may **destroy recall** where it matters most. The language-code findings also suggest that some “language coverage” effects in multilingual benchmarks may be confounded by **mislabeled or superset-language** data, impacting any study that assumes labels are correct.