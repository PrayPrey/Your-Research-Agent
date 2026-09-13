"""h-e1 orchestration: generation loop, smoke test, streaming cache, CLI (A-4, A-7)."""
import argparse
import csv
import json
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from constants import (MAX_NEW_TOKENS, MODEL_IDS, N_LAYERS, RESULTS_DIR, SEED,
                       SMOKE_N, V1_DIRECTION_RECORD)
from analysis import corrected_auroc
from data import (format_prompt, label_response, load_triviaqa, load_truthfulqa,
                  stratified_split, write_test_split_locked)
from model import load_model, validate_layout, per_layer_lens_signals

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("h_e1.run")

CACHE_FIELDS = (
    ["example_id", "dataset", "model", "split", "label"]
    + [f"entropy_L{i}" for i in range(1, N_LAYERS + 1)]
    + [f"maxprob_L{i}" for i in range(1, N_LAYERS + 1)]
    + [f"adj_kl_L{i}" for i in range(1, N_LAYERS + 1)]
)

LOADERS = {"triviaqa": load_triviaqa, "truthfulqa": load_truthfulqa}

# D-1 Gap C: donor cache is h-e1's Phase-4-FINALIZED cell (sibling folder),
# NOT the stale pre-h-e1 archive path v1 pointed at. RESULTS_DIR resolves to
# .../docs/youra_research/h-e1-v2/results, so parents[1] is docs/youra_research.
DONOR_CACHE_LLAMA2_TRIVIAQA = str(
    Path(RESULTS_DIR).resolve().parents[1] / "h-e1" / "results"
    / "cache_llama2_triviaqa.csv")


def verify_donor_cache_path():
    """D-5.1 Gap C acceptance: True iff the donor path resolves to the sibling
    h-e1/results finalized cache (1000 rows, splits finalized), with no
    _archive segment."""
    p = Path(DONOR_CACHE_LLAMA2_TRIVIAQA)
    expected = (Path(RESULTS_DIR).resolve().parents[1] / "h-e1" / "results"
                / "cache_llama2_triviaqa.csv")
    if "_archive" in str(p) or p.resolve() != expected.resolve() or not p.exists():
        return False
    df = pd.read_csv(p)
    return len(df) == 1000 and {"selection", "test"} <= set(df["split"])


def sweep_status(model_keys):
    """D-5.2 completion gate: {'{m}/{d}': bool} -- True iff the cell cache
    exists AND its split column is finalized (both selection and test present)."""
    status = {}
    for m in model_keys:
        for d in LOADERS:
            p = Path(f"{RESULTS_DIR}/cache_{m}_{d}.csv")
            status[f"{m}/{d}"] = (
                p.exists()
                and {"selection", "test"} <= set(
                    pd.read_csv(p, usecols=["split"])["split"]))
    return status


def _cache_header_ok(path):
    """True if the file's header row matches CACHE_FIELDS (stale-schema guard)."""
    try:
        with open(path, newline="") as f:
            return f.readline().rstrip("\r\n").split(",") == CACHE_FIELDS
    except OSError:
        return False


def resume_from_cache(path):
    """Existing cache at path -> set of already-written example_id (A-2.1, NFR-6).
    Missing file / header-only / header-mismatch -> empty set. A corrupt or
    partial tail row (killed mid-write) is truncated in place so the caller's
    'a'-mode append never produces a malformed CSV."""
    if not Path(path).exists():
        return set()
    ids = set()
    with open(path, "r+", newline="") as f:
        header = f.readline()
        if header.rstrip("\r\n").split(",") != CACHE_FIELDS:
            return set()          # stale schema; _cache_header_ok routes to "w" mode
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                break             # clean EOF
            if (not line.endswith("\n")
                    or len(next(csv.reader([line]))) != len(CACHE_FIELDS)):
                log.warning(f"resume_from_cache: truncating corrupt/partial tail "
                            f"row at byte {pos}")
                f.seek(pos)
                f.truncate()
                break
            ids.add(int(line.split(",", 1)[0]))
    return ids


def verify_cache_reuse(model, tokenizer, cache_path, dataset, dataset_name,
                       n_check=10):
    """FR-3.5 protocol-identity check: regenerate the first n_check examples
    fresh and compare label_response output to the donor row's label for the
    same example_id. All-consistent -> True; any drift -> False (caller falls
    through to fresh generation, never silently drops the cell)."""
    if not Path(cache_path).exists():
        log.warning(f"verify_cache_reuse: donor missing at {cache_path}")
        return False
    donor = pd.read_csv(cache_path).set_index("example_id")
    for idx in range(min(n_check, len(dataset))):
        text, sig = generate_and_extract(model, tokenizer, dataset[idx],
                                         dataset_name)
        fresh_empty = bool(np.isnan(sig["entropy"]).all())
        if idx not in donor.index:
            if fresh_empty:
                continue          # both sides skipped the empty answer -> consistent
            log.warning(f"verify_cache_reuse: idx={idx} missing in donor but "
                        f"fresh regen produced an answer")
            return False
        if fresh_empty:
            log.warning(f"verify_cache_reuse: idx={idx} present in donor but "
                        f"fresh regen empty")
            return False
        if label_response(dataset[idx], text, dataset_name) != int(
                donor.loc[idx, "label"]):
            log.warning(f"verify_cache_reuse: idx={idx} label mismatch")
            return False
    log.info(f"verify_cache_reuse: {n_check} examples consistent -> reuse OK")
    return True


def generate_and_extract(model, tokenizer, example, dataset_name,
                         max_new_tokens=MAX_NEW_TOKENS):
    """Greedy decode -> teacher-forced re-forward -> per_layer_lens_signals (A-4.1)."""
    prompt = format_prompt(example, dataset_name)
    enc = tokenizer(prompt, return_tensors="pt").to(model.device)
    T_prompt = enc.input_ids.shape[1]
    gen_ids = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False,
                             pad_token_id=tokenizer.eos_token_id)
    answer_slice = slice(T_prompt, gen_ids.shape[1])
    generated_text = tokenizer.decode(gen_ids[0, T_prompt:], skip_special_tokens=True)

    if answer_slice.stop <= answer_slice.start:      # empty answer (immediate EOS)
        log.warning(f"Empty answer span: example_id={example.get('question_id', '?')}")
        nan32 = np.full(N_LAYERS, np.nan)
        return generated_text, {"entropy": nan32, "maxprob": nan32,
                                "adj_kl": nan32, "top1_match": nan32}

    with torch.no_grad():
        out = model(gen_ids, output_hidden_states=True)   # same sequence, no KV reuse
    signals = per_layer_lens_signals(model, out.hidden_states, answer_slice)
    return generated_text, signals


def write_cache_row(writer, example_id, dataset_name, model_key, split_name,
                    label, signals):
    row = {"example_id": example_id, "dataset": dataset_name, "model": model_key,
           "split": split_name, "label": label}
    for i in range(N_LAYERS):
        row[f"entropy_L{i + 1}"] = float(signals["entropy"][i])
        row[f"maxprob_L{i + 1}"] = float(signals["maxprob"][i])
        row[f"adj_kl_L{i + 1}"] = float(signals["adj_kl"][i])
    writer.writerow(row)


def run_sweep(model, tokenizer, model_key, dataset, dataset_name,
              max_new_tokens=MAX_NEW_TOKENS, reuse_cache_path=None):
    """Sweep ALL examples (labels are generation-dependent, so the stratified
    selection/test split is assigned after the pass, then the CSV split column is
    filled and the test split locked). Streaming per-row flush, R7.
    A-2: reuse_cache_path + verified donor -> copy rows in place of generation;
    else append-mode resume by example_id (FR-3.4/3.5, NFR-6)."""
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    path = f"{RESULTS_DIR}/cache_{model_key}_{dataset_name}.csv"
    top1_path = f"{RESULTS_DIR}/top1_agreement_{model_key}_{dataset_name}.npy"
    top1_sum = np.zeros(N_LAYERS, dtype=np.float64)
    n_written = n_skipped = 0
    t0 = time.time()

    if reuse_cache_path and verify_cache_reuse(model, tokenizer, reuse_cache_path,
                                               dataset, dataset_name):
        donor_df = pd.read_csv(reuse_cache_path)
        donor_df["split"] = "pending"       # normalize; idempotent on rerun
        donor_df.to_csv(path, index=False)  # copy into the cell path; donor untouched
        n_written = len(donor_df)
        n_skipped = len(dataset) - len(donor_df)
        log.info(f"{model_key}/{dataset_name}: donor cache reused, {n_written} "
                 f"rows copied, 0 full-sweep GPU calls")
        # top1_match is not a CACHE_FIELDS column -> cannot be reconstructed from
        # the donor CSV. Approximate top1_agreement.npy from n_check fresh
        # regenerations. ponytail: n=10 sample, upgrade = full recompute pass if
        # degeneracy_screen dependence on this file becomes a measured issue.
        n_check, top1_n = 10, 0
        for idx in range(min(n_check, len(dataset))):
            _, sig = generate_and_extract(model, tokenizer, dataset[idx],
                                          dataset_name, max_new_tokens)
            if not np.isnan(sig["entropy"]).all():
                top1_sum += sig["top1_match"]
                top1_n += 1
        if top1_n:
            np.save(top1_path, top1_sum / top1_n)
    else:
        if reuse_cache_path:
            log.warning(f"{model_key}/{dataset_name}: donor verification FAILED "
                        f"-> fresh generation")
        resume_ids = resume_from_cache(path)
        fresh = not Path(path).exists() or not _cache_header_ok(path)
        if resume_ids:
            log.info(f"{model_key}/{dataset_name}: resuming, {len(resume_ids)} "
                     f"rows already cached")
        with open(path, "w" if fresh else "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CACHE_FIELDS)
            if fresh:
                writer.writeheader()
            for idx in range(len(dataset)):
                if idx in resume_ids:
                    continue
                example = dataset[idx]
                text, signals = generate_and_extract(model, tokenizer, example,
                                                     dataset_name, max_new_tokens)
                if np.isnan(signals["entropy"]).all():
                    n_skipped += 1
                    continue
                label = label_response(example, text, dataset_name)
                write_cache_row(writer, idx, dataset_name, model_key, "pending",
                                label, signals)
                f.flush()                                 # no cross-example buffering
                top1_sum += signals["top1_match"]
                n_written += 1
                if (idx + 1) % 100 == 0:
                    log.info(f"{model_key}/{dataset_name}: "
                             f"{idx + 1}/{len(dataset)} ({time.time() - t0:.0f}s)")
        if n_written:
            np.save(top1_path, top1_sum / n_written)
        elif not Path(top1_path).exists():
            log.warning(f"{model_key}/{dataset_name}: no new rows and no existing "
                        f"{Path(top1_path).name} -- analysis will fail without it")

    # Assign stratified selection/test split on the written rows (seed 42)
    df = pd.read_csv(path)
    labels = df["label"].tolist()
    selection_idx, test_idx = stratified_split(labels, SEED)
    split_col = np.array(["test"] * len(df), dtype=object)
    split_col[selection_idx] = "selection"
    df["split"] = split_col
    df.to_csv(path, index=False)
    write_test_split_locked(df.iloc[test_idx]["example_id"].tolist(),
                            dataset_name, model_key)

    n_sel = len(selection_idx)
    log_line = (f"Lens sweep: model={model_key} layers={N_LAYERS} signals=3 "
                f"examples={n_sel} split=selection")
    print(log_line)
    if n_skipped:
        log.warning(f"Skipped {n_skipped} empty-answer-span examples")
    meta = {"model": model_key, "dataset": dataset_name,
            "vocab_size": int(model.config.vocab_size), "log_line": log_line,
            "n_written": n_written, "n_skipped": n_skipped,
            "n_selection": n_sel, "n_test": len(test_idx),
            "elapsed_s": round(time.time() - t0, 1)}
    Path(f"{RESULTS_DIR}/meta_{model_key}_{dataset_name}.json").write_text(
        json.dumps(meta, indent=2))


def smoke_test(model_key, n=SMOKE_N):
    """FR-3.6: n examples, shape assert, peak-memory print. Must pass before full."""
    model, tokenizer = load_model(model_key)
    validate_layout(model)
    ds = load_triviaqa().select(range(n))
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    for i in range(n):
        _, signals = generate_and_extract(model, tokenizer, ds[i], "triviaqa")
        assert signals["entropy"].shape == (N_LAYERS,), "layer-dim mismatch"
    peak_gb = torch.cuda.max_memory_allocated() / 1e9
    print(f"Smoke test: model={model_key} n={n} time={time.time() - t0:.1f}s "
          f"peak_mem={peak_gb:.2f}GB")
    del model
    torch.cuda.empty_cache()
    return True


def check_anchor_and_halt(model_key, dataset_name, cache_df):
    """D-2.1 (FR-4.1/4.2, A2-v2): protocol-internal validity only. ValueError
    on caller-contract violations (pending split, single-class labels). NEVER
    raises SystemExit on any AUROC value. Returns the within-sweep final-layer
    (L32) entropy corrected AUROC; logs the clause-(c) descriptive
    direction-consistency report (ungated)."""
    sel = cache_df[cache_df["split"] == "selection"]
    if sel.empty:
        raise ValueError(
            f"check_anchor_and_halt: no 'selection' rows for "
            f"{model_key}/{dataset_name} -- split finalization must run before "
            f"the anchor check")
    labels = sel["label"].to_numpy()
    scores = sel["entropy_L32"].to_numpy()
    if len(np.unique(labels)) < 2:
        # newer sklearn warns + returns NaN instead of raising here -- make the
        # caller-contract violation explicit either way
        raise ValueError(
            f"check_anchor_and_halt: single-class selection split for "
            f"{model_key}/{dataset_name} -- AUROC undefined")
    try:
        final_auroc, direction = corrected_auroc(labels, scores)
    except ValueError as e:
        raise ValueError(
            f"check_anchor_and_halt: AUROC undefined for "
            f"{model_key}/{dataset_name} (degenerate label split?): {e}") from e

    # clause (c): descriptive, ungated -- never raises on any value/direction
    v1 = V1_DIRECTION_RECORD.get((model_key, dataset_name))
    log.info(f"A2-v2 anchor: {model_key}/{dataset_name} within-sweep final L32 "
             f"entropy AUROC={final_auroc:.4f} direction={direction} "
             f"v1_record_direction={v1} consistent={direction == v1}")
    return final_auroc


def run_model(model_key):
    """A-3.2: smoke -> per-dataset sweep -> anchor check right after each cell
    (halts before the next cell/model on tolerance breach)."""
    smoke_test(model_key)
    model, tokenizer = load_model(model_key)
    validate_layout(model)
    for dataset_name, loader in LOADERS.items():
        reuse_path = (DONOR_CACHE_LLAMA2_TRIVIAQA
                      if (model_key, dataset_name) == ("llama2", "triviaqa")
                      else None)
        run_sweep(model, tokenizer, model_key, loader(), dataset_name,
                  reuse_cache_path=reuse_path)
        cache_path = f"{RESULTS_DIR}/cache_{model_key}_{dataset_name}.csv"
        final_auroc = check_anchor_and_halt(model_key, dataset_name,
                                            pd.read_csv(cache_path))
        log.info(f"{model_key}/{dataset_name}: cell complete, "
                 f"final_auroc={final_auroc:.4f}")
    del model
    torch.cuda.empty_cache()


def analyze_all(model_keys):
    """Analysis + figures + gate verdict from caches (selection split only)."""
    from analysis import (build_auroc_grid, degeneracy_screen, evaluate_gate,
                          verify_mechanism_activated, write_cell_report)
    import visualize

    gate_results, auroc_grids, retained_map, mechanisms = {}, {}, {}, {}
    rows = []
    for model_key in model_keys:
        for dataset_name in LOADERS:
            cache = f"{RESULTS_DIR}/cache_{model_key}_{dataset_name}.csv"
            meta = json.loads(Path(
                f"{RESULTS_DIR}/meta_{model_key}_{dataset_name}.json").read_text())
            df = pd.read_csv(cache)
            sel = df[df["split"] == "selection"]
            entropy_grid = sel[[f"entropy_L{i}" for i in
                                range(1, N_LAYERS + 1)]].to_numpy()
            top1 = np.load(
                f"{RESULTS_DIR}/top1_agreement_{model_key}_{dataset_name}.npy")
            retained = degeneracy_screen(entropy_grid, top1, meta["vocab_size"])
            grid = build_auroc_grid(df, retained)
            counts = {"positive": int((sel["label"] == 1).sum()),
                      "negative": int((sel["label"] == 0).sum())}
            report = write_cell_report(model_key, dataset_name, grid, retained, counts)
            gate = report["gate"]

            cell_signals = {"entropy": entropy_grid.mean(axis=0),
                            "model_key": model_key, "dataset_name": dataset_name,
                            "final_layer_entropy_auroc":
                                gate["final_layer_entropy_auroc"]
                                if gate["final_layer_entropy_auroc"] is not None
                                else float("nan")}
            mech_ok, mech_detail = verify_mechanism_activated(
                cell_signals, grid, meta["log_line"])

            cell = f"{model_key}/{dataset_name}"
            gate_results[cell] = {k: (float("nan") if v is None else v)
                                  for k, v in gate.items()}
            auroc_grids[cell], retained_map[cell] = grid, retained
            mechanisms[cell] = {"all_true": mech_ok, **mech_detail}
            for i, l in enumerate(retained):
                for j, sig in enumerate(["entropy", "maxprob", "adj_kl"]):
                    rows.append({"model": model_key, "dataset": dataset_name,
                                 "layer": l + 1, "signal": sig,
                                 "corrected_auroc": grid[i, j]})

    figs = [visualize.plot_gate_bar_chart(gate_results),
            visualize.plot_auroc_heatmap(auroc_grids, retained_map),
            visualize.plot_auroc_vs_depth(auroc_grids, retained_map),
            visualize.plot_degeneracy_report(retained_map)]

    out_dir = Path(__file__).parent / "outputs"
    out_dir.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(out_dir / "results.csv", index=False)

    # Overall MUST_WORK verdict: every model passes gate on BOTH datasets
    per_model = {m: all(gate_results[f"{m}/{d}"]["gate_pass"] for d in LOADERS)
                 for m in model_keys}
    overall = all(per_model.values())
    print("\n===== h-e1 GATE REPORT =====")
    for cell in sorted(gate_results):
        g = gate_results[cell]
        print(f"{cell}: best L{g['best_layer']} {g['best_signal']} "
              f"AUROC={g['best_auroc']:.4f} pass={g['gate_pass']} "
              f"final={g['final_layer_entropy_auroc']:.4f} "
              f"depth_beats_final={g['depth_beats_final']} "
              f"mechanism={mechanisms[cell]['all_true']}")
    print(f"Per-model gate: {per_model}")
    print(f"OVERALL MUST_WORK: {'PASS' if overall else 'FAIL'}")

    summary = {"hypothesis_id": "h-e1", "gate_type": "MUST_WORK",
               "overall_pass": overall, "per_model_pass": per_model,
               "cells": {c: {"gate": {k: (None if isinstance(v, float) and
                                          np.isnan(v) else v)
                                      for k, v in gate_results[c].items()},
                             "mechanism": mechanisms[c],
                             "retained_layers": [l + 1 for l in retained_map[c]]}
                         for c in gate_results},
               "figures": [str(p) for p in figs]}
    results_path = Path(RESULTS_DIR).parent / "experiment_results.json"
    results_path.write_text(json.dumps(summary, indent=2))
    print(f"Wrote {results_path}")
    return summary


def build_parser():
    p = argparse.ArgumentParser(description="h-e1 per-layer logit-lens sweep")
    p.add_argument("--model", choices=["llama2", "mistral", "llama3", "all"],
                   required=True)
    p.add_argument("--smoke", action="store_true",
                   help="run SMOKE_N-example smoke test only (FR-3.6)")
    p.add_argument("--full", action="store_true",
                   help="smoke + full sweep over both datasets")
    p.add_argument("--analyze", action="store_true",
                   help="run analysis + figures from existing caches")
    return p


def main():
    args = build_parser().parse_args()
    torch.manual_seed(SEED)
    model_keys = list(MODEL_IDS) if args.model == "all" else [args.model]

    if args.full and "llama2" in model_keys:
        # A-3.2 pre-flight: zero GPU, no model load. Only fires on a RERUN where
        # cache_llama2_triviaqa.csv is already finalized on disk. On a first-ever
        # run the file doesn't exist -> skipped; the anchor is then checked inside
        # run_model("llama2") right after the donor-reuse sweep finalizes.
        early_path = Path(f"{RESULTS_DIR}/cache_llama2_triviaqa.csv")
        if early_path.exists():
            df = pd.read_csv(early_path)
            if "selection" in set(df["split"]):
                check_anchor_and_halt("llama2", "triviaqa", df)

    if args.smoke and not args.full:
        for mk in model_keys:
            smoke_test(mk)
    if args.full:
        for mk in model_keys:
            run_model(mk)
    if args.analyze or (args.full and args.model == "all"):
        summary = analyze_all(list(MODEL_IDS))
        # D-2.2 Gap B wiring: whole-run verifier, log-only -- reported beside
        # overall_pass, never merged into it (FR-4.7 vs FR-4.6 separation).
        from analysis import verify_v2_run_complete
        log_path = Path(__file__).parent / "experiment.log"
        exp_log = log_path.read_text() if log_path.exists() else ""
        v2_ok, v2_detail = verify_v2_run_complete(
            exp_log, {**summary, "completed_cells": list(summary["cells"])})
        log.info(f"verify_v2_run_complete: pass={v2_ok} detail={v2_detail}")
        # persist the 5-indicator result alongside overall_pass (D-6.2 rule 4);
        # re-write keeps analyze_all itself 0-edit
        summary["verify_v2_run_complete"] = {"all_true": v2_ok, **v2_detail}
        results_path = Path(RESULTS_DIR).parent / "experiment_results.json"
        results_path.write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
