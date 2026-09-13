"""Data loaders for all benchmark sources."""
import json
import logging
import re
from pathlib import Path

import pandas as pd

from .matrix import standardize_model_name


def load_trustllm(results_dir: str | Path) -> dict[str, dict[str, float]]:
    """
    Parse TrustLLM results JSONs for BBQ (disambig/ambig) and ANLI (R1/R3) scores.

    Returns:
        {canonical_model_name: {"BBQ-Disambig": float, "BBQ-Ambig": float,
                                 "ANLI-R1": float, "ANLI-R3": float}}
    """
    results_dir = Path(results_dir)
    scores: dict[str, dict[str, float]] = {}

    def _set(model: str, key: str, val: float) -> None:
        scores.setdefault(model, {})[key] = val

    # BBQ scores from Fairness results
    for json_file in results_dir.glob("**/Fairness/**/*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
        except Exception as e:
            logging.warning(f"Failed to parse {json_file}: {e}")
            continue

        if isinstance(data, list):
            for record in data:
                if not isinstance(record, dict):
                    continue
                model = standardize_model_name(str(record.get("model", "")))
                cond = record.get("context_condition", "")
                acc = record.get("accuracy", record.get("acc"))
                if acc is None or not model:
                    continue
                try:
                    acc = float(acc)
                    acc = acc / 100.0 if acc > 1.0 else acc
                except (ValueError, TypeError):
                    continue
                if cond == "disambig":
                    _set(model, "BBQ-Disambig", acc)
                elif cond == "ambig":
                    _set(model, "BBQ-Ambig", acc)
        elif isinstance(data, dict):
            for raw_model, val in data.items():
                model = standardize_model_name(raw_model)
                if isinstance(val, dict):
                    for cond_key, acc in val.items():
                        if acc is None:
                            continue
                        try:
                            acc = float(acc)
                            acc = acc / 100.0 if acc > 1.0 else acc
                        except (ValueError, TypeError):
                            continue
                        if "disambig" in cond_key.lower():
                            _set(model, "BBQ-Disambig", acc)
                        elif "ambig" in cond_key.lower():
                            _set(model, "BBQ-Ambig", acc)

    # ANLI scores from Robustness results
    for json_file in results_dir.glob("**/Robustness/**/*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
        except Exception as e:
            logging.warning(f"Failed to parse {json_file}: {e}")
            continue

        if isinstance(data, list):
            for record in data:
                if not isinstance(record, dict):
                    continue
                model = standardize_model_name(str(record.get("model", "")))
                task = str(record.get("task", record.get("dataset", "")))
                acc = record.get("accuracy", record.get("acc"))
                if acc is None or not model:
                    continue
                try:
                    acc = float(acc)
                    acc = acc / 100.0 if acc > 1.0 else acc
                except (ValueError, TypeError):
                    continue
                tl = task.lower()
                if "anli" in tl and "r1" in tl:
                    _set(model, "ANLI-R1", acc)
                elif "anli" in tl and "r3" in tl:
                    _set(model, "ANLI-R3", acc)
        elif isinstance(data, dict):
            for raw_model, task_dict in data.items():
                model = standardize_model_name(raw_model)
                if not isinstance(task_dict, dict):
                    continue
                for task_key, acc in task_dict.items():
                    if acc is None:
                        continue
                    try:
                        acc = float(acc)
                        acc = acc / 100.0 if acc > 1.0 else acc
                    except (ValueError, TypeError):
                        continue
                    tl = task_key.lower()
                    if "anli" in tl and "r1" in tl:
                        _set(model, "ANLI-R1", acc)
                    elif "anli" in tl and "r3" in tl:
                        _set(model, "ANLI-R3", acc)

    logging.info(f"TrustLLM: loaded {len(scores)} models from {results_dir}")
    return scores


def load_glue_x(data_path: str | Path) -> dict[str, dict[str, float]]:
    """
    Extract GLUE (ID) and AdvGLUE (OOD) average scores per model from GLUE-X data.

    WARNING: GLUE-X evaluates PLMs, NOT decoder-only LLMs.
    Model overlap with TrustLLM set expected to be minimal.
    """
    data_path = Path(data_path)
    scores: dict[str, dict[str, float]] = {}

    if not data_path.exists():
        logging.warning(f"GLUE-X path not found: {data_path}")
        return scores

    if data_path.suffix == ".csv":
        try:
            df = pd.read_csv(data_path)
        except Exception as e:
            logging.warning(f"Failed to read GLUE-X CSV {data_path}: {e}")
            return scores

        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
        model_col = next((c for c in df.columns if "model" in c), df.columns[0])
        glue_col = next((c for c in df.columns if "glue" in c and "adv" not in c), None)
        advglue_col = next((c for c in df.columns if "adv" in c or "ood" in c), None)

        for _, row in df.iterrows():
            model = standardize_model_name(str(row[model_col]))
            entry: dict[str, float] = {}
            if glue_col and pd.notna(row.get(glue_col)):
                val = float(row[glue_col])
                entry["GLUE"] = val / 100.0 if val > 1.0 else val
            if advglue_col and pd.notna(row.get(advglue_col)):
                val = float(row[advglue_col])
                entry["AdvGLUE"] = val / 100.0 if val > 1.0 else val
            if entry:
                scores[model] = entry

    elif data_path.suffix == ".pdf":
        try:
            import pdfplumber
            with pdfplumber.open(data_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    for match in re.finditer(
                        r"([A-Za-z0-9\-\.]+(?:\-large|\-base|\-small)?)\s+"
                        r"(\d{1,2}\.\d{1,2})\s+(\d{1,2}\.\d{1,2})",
                        text,
                    ):
                        model = standardize_model_name(match.group(1))
                        scores[model] = {
                            "GLUE": float(match.group(2)) / 100.0,
                            "AdvGLUE": float(match.group(3)) / 100.0,
                        }
        except ImportError:
            logging.warning("pdfplumber not installed; cannot parse PDF GLUE-X data")
        except Exception as e:
            logging.warning(f"PDF parse error: {e}")
    else:
        logging.warning(f"Unsupported GLUE-X format: {data_path.suffix}")

    logging.info(f"GLUE-X: loaded {len(scores)} models from {data_path}")
    return scores


def load_hf_leaderboard(
    parquet_url: str = "hf://datasets/OpenEvals/leaderboard-data/data/train-00000-of-00001.parquet",
    mmlu_col: str | None = None,
) -> dict[str, dict[str, float]]:
    """Load MMLU scores from HuggingFace leaderboard parquet."""
    scores: dict[str, dict[str, float]] = {}
    try:
        df = pd.read_parquet(parquet_url)
    except Exception as e:
        logging.warning(f"HF parquet load failed: {e}. Returning empty dict.")
        return scores

    if mmlu_col is None:
        candidates = [c for c in df.columns if "mmlu" in c.lower()]
        original = [c for c in candidates if "pro" not in c.lower()]
        mmlu_col = original[0] if original else (candidates[0] if candidates else None)

    if mmlu_col is None:
        logging.warning("No MMLU column found in HF leaderboard parquet.")
        return scores

    model_col = next((c for c in df.columns if "model" in c.lower()), df.columns[0])
    for _, row in df.iterrows():
        if pd.isna(row.get(mmlu_col)):
            continue
        model = standardize_model_name(str(row[model_col]))
        try:
            val = float(row[mmlu_col])
            scores[model] = {"MMLU": val / 100.0 if val > 1.0 else val}
        except (ValueError, TypeError):
            continue

    logging.info(f"HF Leaderboard: loaded {len(scores)} models")
    return scores


def load_ood_nlp(results_dir: str | Path) -> dict[str, dict[str, float]]:
    """Load ANLI-R1, ANLI-R3 supplement from lifan-yuan/OOD_NLP repository."""
    results_dir = Path(results_dir)
    scores: dict[str, dict[str, float]] = {}

    if not results_dir.exists():
        logging.warning(f"OOD_NLP dir not found: {results_dir}")
        return scores

    pattern = re.compile(r"anli", re.IGNORECASE)
    for f in results_dir.rglob("*"):
        if f.suffix not in (".json", ".csv"):
            continue
        if not pattern.search(f.name):
            continue
        try:
            if f.suffix == ".json":
                with open(f) as fh:
                    data = json.load(fh)
                records = data if isinstance(data, list) else [data]
            else:
                records = pd.read_csv(f).to_dict("records")

            for record in records:
                if not isinstance(record, dict):
                    continue
                model = standardize_model_name(str(record.get("model", "")))
                if not model:
                    continue
                for key, val in record.items():
                    if val is None:
                        continue
                    kl = key.lower()
                    try:
                        fval = float(val)
                        fval = fval / 100.0 if fval > 1.0 else fval
                    except (ValueError, TypeError):
                        continue
                    if "anli" in kl and "r1" in kl:
                        scores.setdefault(model, {})["ANLI-R1"] = fval
                    elif "anli" in kl and "r3" in kl:
                        scores.setdefault(model, {})["ANLI-R3"] = fval
        except Exception as e:
            logging.warning(f"Failed to parse {f}: {e}")

    logging.info(f"OOD_NLP: loaded {len(scores)} models from {results_dir}")
    return scores


def load_decoding_trust(results_dir: str | Path) -> dict[str, dict[str, float]]:
    """
    Load AdvGLUE++ and fairness scores from AI-secure/DecodingTrust.
    Covers GPT-3.5-Turbo, GPT-4.
    """
    results_dir = Path(results_dir)
    scores: dict[str, dict[str, float]] = {}

    if not results_dir.exists():
        logging.warning(f"DecodingTrust dir not found: {results_dir}")
        return scores

    for f in results_dir.rglob("*"):
        if f.suffix not in (".json", ".csv"):
            continue
        name_lower = f.name.lower()
        if not any(k in name_lower for k in ("advglue", "fairness", "bbq")):
            continue
        try:
            if f.suffix == ".json":
                with open(f) as fh:
                    data = json.load(fh)
                records = data if isinstance(data, list) else [data]
            else:
                records = pd.read_csv(f).to_dict("records")

            for record in records:
                if not isinstance(record, dict):
                    continue
                model = standardize_model_name(str(record.get("model", "")))
                if not model:
                    continue
                for key, val in record.items():
                    if val is None:
                        continue
                    kl = key.lower()
                    try:
                        fval = float(val)
                        fval = fval / 100.0 if fval > 1.0 else fval
                    except (ValueError, TypeError):
                        continue
                    if "advglue" in kl:
                        scores.setdefault(model, {})["AdvGLUE"] = fval
                    elif "disambig" in kl or ("bbq" in kl and "disambig" in kl):
                        scores.setdefault(model, {})["BBQ-Disambig"] = fval
                    elif "ambig" in kl or "bbq" in kl:
                        scores.setdefault(model, {})["BBQ-Ambig"] = fval
        except Exception as e:
            logging.warning(f"Failed to parse {f}: {e}")

    logging.info(f"DecodingTrust: loaded {len(scores)} models from {results_dir}")
    return scores
