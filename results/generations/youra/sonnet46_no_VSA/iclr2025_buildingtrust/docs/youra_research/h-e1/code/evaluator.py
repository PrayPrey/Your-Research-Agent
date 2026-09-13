"""Adversarial evaluation for H-E1."""
import logging
import re

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger(__name__)

# AdvGLUE attack method → category ID
ATTACK_CATEGORY_MAP = {
    "textfooler":  "C1",
    "pwws":        "C2",
    "bert-attack": "C3",
    "semattack":   "C4",
    "charswap":    "C5",
    "distraction": "C6",
    "syntactic":   "C7",
    "human":       "C8",
    "checklist_inv": "C9",
    "checklist_dir": "C10",
    "checklist_mft": "C11",
}

EXTRA_CATEGORIES = ["ANLI-R3", "CheckList"]
ADV_TASK_CATEGORIES = ["adv_sst2", "adv_mnli", "adv_qqp", "adv_qnli", "adv_rte"]
ATTACK_CATEGORIES = [f"C{i}" for i in range(1, 12)] + EXTRA_CATEGORIES + ADV_TASK_CATEGORIES

TASK_ATTACK_SUPPORT = {
    "sst2":  [f"C{i}" for i in range(1, 9)],
    "mnli":  [f"C{i}" for i in range(1, 9)] + ["ANLI-R3"],
    "qqp":   [f"C{i}" for i in range(1, 9)],
    "qnli":  [f"C{i}" for i in range(1, 9)],
    "rte":   [f"C{i}" for i in range(1, 9)],
}

# Map adv_glue dataset "method" field values (may vary) to categories
_METHOD_ALIASES = {
    "textfooler": "C1", "text_fooler": "C1",
    "pwws": "C2",
    "bert_attack": "C3", "bert-attack": "C3",
    "semattack": "C4", "sem_attack": "C4",
    "charswap": "C5", "char_swap": "C5",
    "distraction": "C6",
    "syntactic": "C7",
    "human": "C8",
}


def _load_model_and_tokenizer(model_path: str, tokenizer_id: str, num_labels: int = 2):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "left"

    model = AutoModelForSequenceClassification.from_pretrained(
        model_path, num_labels=num_labels
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    return model, tokenizer, device


def _predict_batch(texts, model, tokenizer, device, batch_size: int = 32, task: str = "sst2", texts2=None):
    all_preds = []
    for i in range(0, len(texts), batch_size):
        batch_t = texts[i:i+batch_size]
        if texts2 is not None:
            batch_t2 = texts2[i:i+batch_size]
            enc = tokenizer(batch_t, batch_t2, truncation=True, max_length=128,
                            padding=True, return_tensors="pt")
        else:
            enc = tokenizer(batch_t, truncation=True, max_length=128,
                            padding=True, return_tensors="pt")
        enc = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            logits = model(**enc).logits
        preds = logits.argmax(dim=-1).cpu().numpy()
        all_preds.extend(preds.tolist())
    return np.array(all_preds)


def _extract_texts_labels(dataset, task: str):
    """Extract (texts, texts2, labels) from a HF dataset depending on task."""
    cols = dataset.column_names if hasattr(dataset, "column_names") else []
    labels = np.array(dataset["label"]) if "label" in cols else None

    if task == "sst2":
        text_col = "sentence" if "sentence" in cols else "text"
        return dataset[text_col], None, labels
    elif task in ("mnli", "rte"):
        c1 = "premise" if "premise" in cols else "sentence1"
        c2 = "hypothesis" if "hypothesis" in cols else "sentence2"
        return dataset[c1], dataset[c2], labels
    elif task == "qnli":
        c1 = "question" if "question" in cols else "sentence1"
        c2 = "sentence" if "sentence" in cols else "sentence2"
        return dataset[c1], dataset[c2], labels
    elif task == "qqp":
        c1 = "question1" if "question1" in cols else "sentence1"
        c2 = "question2" if "question2" in cols else "sentence2"
        return dataset[c1], dataset[c2], labels
    return dataset["text"], None, labels


def evaluate_on_dataset(
    model_path: str,
    tokenizer_id: str,
    dataset,
    task: str,
    batch_size: int = 32,
    num_labels: int = None,
) -> float:
    if num_labels is None:
        from data_loader import get_num_labels
        num_labels = get_num_labels(task)

    model, tokenizer, device = _load_model_and_tokenizer(model_path, tokenizer_id, num_labels)
    texts, texts2, labels = _extract_texts_labels(dataset, task)

    if labels is None or len(labels) == 0:
        return 0.0

    labels = np.array([int(l) for l in labels])
    preds = _predict_batch(texts, model, tokenizer, device, batch_size, task, texts2)
    acc = float((preds == labels).mean())
    del model
    torch.cuda.empty_cache()
    return acc


def evaluate_adv_glue(
    model_path: str,
    tokenizer_id: str,
    adv_data: dict,
    batch_size: int = 32,
) -> dict:
    """Returns {attack_category: adv_accuracy} aggregated across tasks."""
    from data_loader import get_num_labels

    category_hits = {}
    category_totals = {}

    for task, ds in adv_data.items():
        num_labels = get_num_labels(task)
        model, tokenizer, device = _load_model_and_tokenizer(model_path, tokenizer_id, num_labels)
        texts, texts2, labels = _extract_texts_labels(ds, task)

        if labels is None or len(labels) == 0:
            del model; torch.cuda.empty_cache()
            continue

        labels = np.array([int(l) for l in labels])
        cols = ds.column_names if hasattr(ds, "column_names") else []

        # Determine per-example category from "method" field
        if "method" in cols:
            methods = ds["method"]
            cat_map = {}
            for j, m in enumerate(methods):
                if m is None:
                    continue
                m_lower = str(m).lower().replace(" ", "_")
                cat = _METHOD_ALIASES.get(m_lower) or _METHOD_ALIASES.get(m.lower())
                if cat:
                    cat_map.setdefault(cat, []).append(j)
            # Evaluate per category
            for cat, idxs in cat_map.items():
                idx_arr = np.array(idxs)
                t = [texts[i] for i in idx_arr]
                t2 = [texts2[i] for i in idx_arr] if texts2 is not None else None
                l = labels[idx_arr]
                preds = _predict_batch(t, model, tokenizer, device, batch_size, task, t2)
                category_hits[cat] = category_hits.get(cat, 0) + int((preds == l).sum())
                category_totals[cat] = category_totals.get(cat, 0) + len(l)
        else:
            # No method field — treat entire task dataset as one category (task-based)
            # Use task name as category key so we get per-task adversarial scores
            preds = _predict_batch(texts, model, tokenizer, device, batch_size, task, texts2)
            cat = f"adv_{task}"
            category_hits[cat] = category_hits.get(cat, 0) + int((preds == labels).sum())
            category_totals[cat] = category_totals.get(cat, 0) + len(labels)

        del model
        torch.cuda.empty_cache()

    result = {}
    for cat in list(category_totals.keys()):
        if category_totals[cat] > 0:
            result[cat] = category_hits[cat] / category_totals[cat]

    return result


def evaluate_anli_r3(
    model_path: str,
    tokenizer_id: str,
    dataset,
    batch_size: int = 32,
) -> float:
    """Evaluate on ANLI-R3 (NLI = 3-class)."""
    model, tokenizer, device = _load_model_and_tokenizer(model_path, tokenizer_id, num_labels=3)
    cols = dataset.column_names if hasattr(dataset, "column_names") else []

    prem_col = "premise" if "premise" in cols else "context"
    hyp_col = "hypothesis" if "hypothesis" in cols else "hypothesis"
    label_col = "label" if "label" in cols else "gold_label"

    texts = dataset[prem_col]
    texts2 = dataset[hyp_col]
    labels = np.array(dataset[label_col])

    preds = _predict_batch(texts, model, tokenizer, device, batch_size, "mnli", texts2)
    acc = float((preds == labels).mean())
    del model; torch.cuda.empty_cache()
    return acc


def evaluate_checklist(
    model_path: str,
    tokenizer_id: str,
    suites: list,
    batch_size: int = 32,
) -> dict:
    """Returns {suite_name: accuracy}."""
    if not suites:
        return {}

    results = {}
    for suite in suites:
        examples = suite.get("examples", [])
        labels = suite.get("labels", [])
        name = suite.get("name", "unknown")

        if not examples or not labels:
            continue

        # Determine num_labels from suite
        unique_labels = set(labels)
        num_labels = max(unique_labels) + 1 if unique_labels else 2

        try:
            model, tokenizer, device = _load_model_and_tokenizer(
                model_path, tokenizer_id, num_labels=num_labels
            )
            # CheckList examples may be strings or tuples
            if isinstance(examples[0], (list, tuple)):
                texts = [str(e[0]) for e in examples]
                texts2 = [str(e[1]) for e in examples]
            else:
                texts = [str(e) for e in examples]
                texts2 = None

            l_arr = np.array(labels)
            preds = _predict_batch(texts, model, tokenizer, device, batch_size, "sst2", texts2)
            acc = float((preds == l_arr).mean())
            results[name] = acc
            del model; torch.cuda.empty_cache()
        except Exception as e:
            logger.warning(f"CheckList suite {name} eval failed: {e}")
            continue

    return results


def run_all_evaluations(
    finetuned: dict,
    adv_data: dict,
    anli_data,
    checklist_suites: list,
    clean_data: dict = None,
    checkpoint_dir: str = None,
) -> dict:
    """Returns {model_id: {attack_category: {"clean_acc": float, "adv_acc": float}}}.
    
    Saves per-model partial results to checkpoint_dir/eval_partial_{model_id_safe}.json
    so crashes mid-run can be resumed.
    """
    import json, os
    from fine_tuner import MODEL_CONFIGS
    from data_loader import get_num_labels

    all_results = {}

    # Load any existing partial results
    partial_done = set()
    if checkpoint_dir:
        os.makedirs(checkpoint_dir, exist_ok=True)
        for model_id in finetuned:
            safe = model_id.replace("/", "_")
            p = os.path.join(checkpoint_dir, f"eval_partial_{safe}.json")
            if os.path.exists(p):
                with open(p) as f:
                    all_results[model_id] = json.load(f)
                partial_done.add(model_id)
                logger.info(f"Loaded partial eval for {model_id} from checkpoint")

    for model_id, task_ckpts in finetuned.items():
        if model_id in partial_done:
            logger.info(f"Skipping {model_id} (already evaluated)")
            continue

        logger.info(f"Evaluating {model_id}")
        all_results[model_id] = {}
        tokenizer_id = model_id

        for task, (ckpt_path, clean_acc) in task_ckpts.items():
            if ckpt_path is None:
                continue

            if clean_acc is None and clean_data and task in clean_data:
                try:
                    clean_acc = evaluate_on_dataset(ckpt_path, tokenizer_id, clean_data[task], task)
                    logger.info(f"{model_id}/{task} clean_acc={clean_acc:.4f}")
                except Exception as e:
                    logger.warning(f"Clean eval failed {model_id}/{task}: {e}")
                    clean_acc = 0.0

            if task in adv_data:
                try:
                    adv_results = evaluate_adv_glue(
                        ckpt_path, tokenizer_id, {task: adv_data[task]}
                    )
                    for cat, adv_acc in adv_results.items():
                        key = f"{task}_{cat}"
                        all_results[model_id][key] = {
                            "clean_acc": clean_acc or 0.0,
                            "adv_acc": adv_acc,
                            "task": task,
                            "category": cat,
                            "n_examples": len(adv_data[task]),
                        }
                    logger.info(f"{model_id}/{task} adv categories: {list(adv_results.keys())}, "
                                f"n={len(adv_data[task])}")
                except Exception as e:
                    logger.warning(f"AdvGLUE eval failed {model_id}/{task}: {e}")

        if "mnli" in task_ckpts and task_ckpts["mnli"][0] is not None:
            ckpt_path, clean_acc = task_ckpts["mnli"]
            try:
                anli_acc = evaluate_anli_r3(ckpt_path, tokenizer_id, anli_data)
                all_results[model_id]["anli_ANLI-R3"] = {
                    "clean_acc": clean_acc or 0.0,
                    "adv_acc": anli_acc,
                    "task": "mnli",
                    "category": "ANLI-R3",
                    "n_examples": len(anli_data),
                }
                logger.info(f"{model_id} ANLI-R3 acc={anli_acc:.4f}")
            except Exception as e:
                logger.warning(f"ANLI-R3 eval failed {model_id}: {e}")

        if checklist_suites and "sst2" in task_ckpts and task_ckpts["sst2"][0] is not None:
            ckpt_path, clean_acc = task_ckpts["sst2"]
            try:
                cl_results = evaluate_checklist(ckpt_path, tokenizer_id, checklist_suites)
                for suite_name, acc in cl_results.items():
                    all_results[model_id][f"cl_{suite_name}"] = {
                        "clean_acc": clean_acc or 0.0,
                        "adv_acc": acc,
                        "task": "sst2",
                        "category": "CheckList",
                        "n_examples": 0,
                    }
            except Exception as e:
                logger.warning(f"CheckList eval failed {model_id}: {e}")

        # Save per-model partial checkpoint
        if checkpoint_dir:
            safe = model_id.replace("/", "_")
            p = os.path.join(checkpoint_dir, f"eval_partial_{safe}.json")
            with open(p, "w") as f:
                json.dump(all_results[model_id], f, indent=2)
            logger.info(f"Saved partial eval checkpoint for {model_id}")

    return all_results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("ATTACK_CATEGORIES:", ATTACK_CATEGORIES)
    print("Total categories:", len(ATTACK_CATEGORIES))
