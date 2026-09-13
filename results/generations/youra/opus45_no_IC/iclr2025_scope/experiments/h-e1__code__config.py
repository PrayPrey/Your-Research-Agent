"""H-E1 Configuration: LongBench tasks and compression configs."""

TASKS = [
    "narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh",
    "hotpotqa", "2wikimqa", "musique", "dureader",
    "gov_report", "qmsum", "multi_news", "vcsum",
    "trec", "triviaqa", "samsum", "lsht",
    "passage_retrieval_en", "passage_count", "passage_retrieval_zh",
    "lcc", "repobench-p",
]

COMPRESSION_CONFIGS = [
    {"name": "C1_full", "method": "full", "retention": 1.0, "quantization": None},
    {"name": "C2_h2o80", "method": "h2o", "retention": 0.8, "quantization": None},
    {"name": "C3_h2o40", "method": "h2o", "retention": 0.4, "quantization": None},
    {"name": "C4_full_int8", "method": "full", "retention": 1.0, "quantization": "int8"},
    {"name": "C5_full_int4", "method": "full", "retention": 1.0, "quantization": "int4"},
    {"name": "C6_h2o60_int8", "method": "h2o", "retention": 0.6, "quantization": "int8"},
]

MODEL_ID = "meta-llama/Llama-2-7b-hf"
MAX_TOKENS = 4096
MAX_NEW_TOKENS = 128
SEED = 42

GAP_STATISTIC = {"n_refs": 500, "max_k": 6}

TASK_METRIC = {
    "narrativeqa": "qa_f1_score", "qasper": "qa_f1_score",
    "multifieldqa_en": "qa_f1_score", "multifieldqa_zh": "qa_f1_score",
    "hotpotqa": "qa_f1_score", "2wikimqa": "qa_f1_score",
    "musique": "qa_f1_score", "dureader": "rouge_score",
    "gov_report": "rouge_score", "qmsum": "rouge_score",
    "multi_news": "rouge_score", "vcsum": "rouge_score",
    "trec": "classification_score", "triviaqa": "qa_f1_score",
    "samsum": "rouge_score", "lsht": "classification_score",
    "passage_retrieval_en": "retrieval_score", "passage_count": "qa_f1_score",
    "passage_retrieval_zh": "retrieval_score",
    "lcc": "code_sim_score", "repobench-p": "code_sim_score",
}

TASK_CATEGORIES = {
    "single_doc_qa": ["narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh"],
    "multi_doc_qa": ["hotpotqa", "2wikimqa", "musique", "dureader"],
    "summarization": ["gov_report", "qmsum", "multi_news", "vcsum"],
    "fewshot": ["trec", "triviaqa", "samsum", "lsht"],
    "synthetic": ["passage_retrieval_en", "passage_count", "passage_retrieval_zh"],
    "code": ["lcc", "repobench-p"],
}
