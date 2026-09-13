import json
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import ExperimentConfig


# ─── Checkpoint-Resume Helpers ────────────────────────────────────────────────

def _get_completed_ids_jsonl(filepath: str) -> Set[int]:
    path = Path(filepath)
    if not path.exists():
        return set()
    ids = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    ids.add(int(json.loads(line)["id"]))
                except (KeyError, ValueError, json.JSONDecodeError):
                    pass
    return ids


def _get_completed_ids_logits(logits_dir: str) -> Set[int]:
    d = Path(logits_dir)
    if not d.exists():
        return set()
    return {int(p.stem.split("_")[-1]) for p in d.glob("example_*.pt")}


def append_jsonl(record: Dict[str, Any], filepath: str) -> None:
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")


def load_greedy_outputs(outputs_dir: str) -> Dict[int, Dict[str, Any]]:
    path = Path(outputs_dir) / "greedy_responses.jsonl"
    result = {}
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    result[int(rec["id"])] = rec
    return result


def load_stochastic_outputs(outputs_dir: str) -> Dict[int, List[str]]:
    path = Path(outputs_dir) / "stochastic_samples.jsonl"
    result = {}
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    result[int(rec["id"])] = rec["samples"]
    return result


# ─── Model Loading ────────────────────────────────────────────────────────────

def load_llm(cfg: ExperimentConfig) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}
    dtype = dtype_map.get(cfg.llm_dtype, torch.float16)

    # Try local cache first, fall back to network
    try:
        tokenizer = AutoTokenizer.from_pretrained(cfg.llm_model_id, local_files_only=True)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(cfg.llm_model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    try:
        model = AutoModelForCausalLM.from_pretrained(
            cfg.llm_model_id,
            torch_dtype=dtype,
            device_map="auto",
            local_files_only=True,
        )
    except Exception:
        model = AutoModelForCausalLM.from_pretrained(
            cfg.llm_model_id,
            torch_dtype=dtype,
            device_map="auto",
        )
    model.eval()
    return model, tokenizer


def _build_prompt(question: str, answer: str) -> str:
    # Plain QA prompt compatible with base (non-chat) LLaMA-2
    return f"Question: {question}\nAnswer: {answer}"


# ─── Greedy Inference ─────────────────────────────────────────────────────────

def run_greedy_inference(
    examples: List[Dict[str, Any]],
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    cfg: ExperimentConfig,
    resume: bool = True,
) -> None:
    logits_dir = Path(cfg.outputs_dir) / "greedy_logits"
    logits_dir.mkdir(parents=True, exist_ok=True)
    greedy_path = str(Path(cfg.outputs_dir) / "greedy_responses.jsonl")

    completed = _get_completed_ids_logits(str(logits_dir)) if resume else set()
    if completed:
        print(f"Resuming greedy from {len(completed)} completed examples")

    for example in tqdm(examples, desc="Greedy inference"):
        eid = int(example["id"])
        if eid in completed:
            continue

        prompt = _build_prompt(example["question"], example["answer"])
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        input_ids = inputs.input_ids.to(model.device)

        with torch.no_grad():
            output = model.generate(
                input_ids,
                max_new_tokens=cfg.max_new_tokens,
                do_sample=False,
                output_scores=True,
                return_dict_in_generate=True,
            )

        # Stack scores: tuple of [1, vocab_size] → [seq_len, vocab_size]
        if output.scores:
            logits = torch.stack(output.scores, dim=0).squeeze(1)  # [seq_len, vocab_size]
        else:
            logits = torch.zeros(1, model.config.vocab_size)

        response_ids = output.sequences[0, input_ids.shape[1]:]
        response_text = tokenizer.decode(response_ids, skip_special_tokens=True)

        torch.save(logits.cpu().half(), logits_dir / f"example_{eid}.pt")
        append_jsonl({"id": eid, "response": response_text}, greedy_path)


# ─── Stochastic Inference ─────────────────────────────────────────────────────

def run_stochastic_inference(
    examples: List[Dict[str, Any]],
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    cfg: ExperimentConfig,
    resume: bool = True,
) -> None:
    stochastic_path = str(Path(cfg.outputs_dir) / "stochastic_samples.jsonl")
    completed = _get_completed_ids_jsonl(stochastic_path) if resume else set()
    if completed:
        print(f"Resuming stochastic from {len(completed)} completed examples")

    N = cfg.n_stochastic_samples

    for example in tqdm(examples, desc="Stochastic inference"):
        eid = int(example["id"])
        if eid in completed:
            continue

        prompt = _build_prompt(example["question"], example["answer"])
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        input_ids = inputs.input_ids.to(model.device)

        try:
            expanded = input_ids.expand(N, -1)
            with torch.no_grad():
                output = model.generate(
                    expanded,
                    max_new_tokens=cfg.max_new_tokens,
                    do_sample=True,
                    temperature=cfg.stochastic_temperature,
                    renormalize_logits=True,
                )
            gen_ids = output[:, input_ids.shape[1]:]
            samples = [tokenizer.decode(gen_ids[i], skip_special_tokens=True) for i in range(N)]
        except (torch.cuda.OutOfMemoryError, RuntimeError):
            # Fallback: sequential single-sample generation (avoids batch NaN/OOM)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            samples = []
            for _ in range(N):
                with torch.no_grad():
                    out = model.generate(
                        input_ids,
                        max_new_tokens=cfg.max_new_tokens,
                        do_sample=True,
                        temperature=cfg.stochastic_temperature,
                        renormalize_logits=True,
                    )
                gen = out[0, input_ids.shape[1]:]
                samples.append(tokenizer.decode(gen, skip_special_tokens=True))

        append_jsonl({"id": eid, "samples": samples}, stochastic_path)
