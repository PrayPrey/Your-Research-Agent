"""H-E1: Data infrastructure verification pipeline for huashen218 bidirectional-alignment corpus."""
import json
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import requests

from config import (
    API_KEY, BATCH_FIELDS, CORPUS_REPO, COVERAGE_GATE, CROSS_GROUP_GATE,
    HCI_VENUES, MAX_RETRIES, REF_FIELDS, S2AG_BASE, SCHEMES, SLEEP_SECS,
    ML_NLP_VENUES_S1,
)


# ── Corpus Ingestion ──────────────────────────────────────────────────────────

def clone_corpus(dest: str = "corpus") -> Path:
    """Clone the huashen218 reading list repo."""
    dest_path = Path(dest)
    if dest_path.exists() and any(dest_path.iterdir()):
        print(f"  corpus already cloned at {dest_path}")
        return dest_path
    print(f"  cloning {CORPUS_REPO} → {dest_path}")
    result = subprocess.run(
        ["git", "clone", "--depth=1", CORPUS_REPO, str(dest_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"git clone failed: {result.stderr}")
    return dest_path


def extract_paper_ids(corpus_dir: Path) -> list[str]:
    """
    Extract resolvable paper identifiers from all text files in the corpus.
    Returns arXiv IDs, DOIs, ACL anthology IDs, OpenReview IDs, NeurIPS IDs.
    Format: arXiv:XXXX.XXXXX | 10.XXXX/... | ACL:YYYY.XXXXX | OR:XXXXX | NP:XXXXX
    """
    ids: set[str] = set()
    for ext in ("*.md", "*.txt", "*.bib", "*.yaml", "*.yml", "*.json"):
        for f in corpus_dir.rglob(ext):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # arXiv abs and pdf links
            for arxiv_id in re.findall(r'arxiv\.org/(?:abs|pdf)/([\d.]+[v\d]*)', text, re.I):
                clean = re.sub(r'v\d+$', '', arxiv_id)
                ids.add(f"arXiv:{clean}")
            # arXiv in bibtex / colon notation
            for arxiv_id in re.findall(r'arxiv[:\s/]*(?:abs|pdf)[:/\s]*([\d.]+[v\d]*)', text, re.I):
                clean = re.sub(r'v\d+$', '', arxiv_id)
                ids.add(f"arXiv:{clean}")
            # DOI links
            for doi in re.findall(r'doi\.org/(10\.\S+?)(?=[)\s,"\']|$)', text):
                ids.add(doi.rstrip(").,"))
            # ACM DL: dl.acm.org/doi/10.XXXX/...
            for doi in re.findall(r'dl\.acm\.org/doi/(10\.\S+?)(?=[)\s,"\']|$)', text):
                ids.add(doi.rstrip(").,"))
            # ACL anthology: aclanthology.org/YYYY.venue-vol.paper
            for acl_id in re.findall(r'aclanthology\.org/([A-Z0-9]{4}\.[a-z0-9\-]+)', text):
                ids.add(f"ACL:{acl_id}")
            # OpenReview: openreview.net/forum?id=XXXXX or /pdf?id=XXXXX
            for or_id in re.findall(r'openreview\.net/(?:forum|pdf)\?id=([A-Za-z0-9_\-]+)', text):
                ids.add(f"OR:{or_id}")
            # NeurIPS proceedings: proceedings.neurips.cc/paper/YYYY/hash/XXXX
            for np_match in re.findall(r'proceedings\.neurips\.cc/paper(?:_files)?/paper/(\d{4})/hash/([a-f0-9]+)', text, re.I):
                ids.add(f"NP:{np_match[0]}/{np_match[1]}")

    result = list(ids)
    print(f"  extracted {len(result)} unique paper IDs from {corpus_dir}")
    return result


# ── S2AG API ──────────────────────────────────────────────────────────────────

def _make_headers() -> dict:
    return {"x-api-key": API_KEY} if API_KEY else {}


def _api_get(url: str, params: dict, cache_path: Path) -> dict | list:
    """Cache-aside GET with 3-retry exponential backoff."""
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, params=params, headers=_make_headers(), timeout=30)
            if resp.status_code == 404:
                cache_path.write_text(json.dumps({}))
                return {}
            if resp.status_code == 429:
                wait = 60 * (attempt + 1)
                print(f"    rate-limited; sleeping {wait}s")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            cache_path.write_text(json.dumps(data))
            time.sleep(SLEEP_SECS)
            return data
        except requests.RequestException as exc:
            print(f"    request error (attempt {attempt+1}/{MAX_RETRIES}): {exc}")
            time.sleep(2 ** attempt)
    return {}


def _normalize_id_for_s2ag(input_id: str) -> str:
    """Convert internal ID format to S2AG-compatible format."""
    if input_id.startswith("arXiv:"):
        return input_id  # S2AG accepts arXiv:XXXX.XXXXX natively
    if input_id.startswith("ACL:"):
        return f"ACL:{input_id[4:]}"  # S2AG: ACL:YYYY.venue-vol.paper
    if input_id.startswith("OR:"):
        # OpenReview IDs not directly supported; use as-is (S2AG may reject)
        return input_id[3:]  # pass raw ID, S2AG will try
    if input_id.startswith("NP:"):
        return input_id[3:]  # NeurIPS hash, may not resolve
    if input_id.startswith("10."):
        return f"DOI:{input_id}"  # DOI format for S2AG
    return input_id


def resolve_papers(ids: list[str], cache_dir: Path) -> dict[str, dict | None]:
    """Batch-resolve paper IDs via POST /paper/batch (≤500 per chunk)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict | None] = {}
    # Normalize IDs for S2AG
    id_map = {_normalize_id_for_s2ag(pid): pid for pid in ids}  # s2ag_id -> input_id
    s2ag_ids = list(id_map.keys())
    chunk_size = 500
    chunks = [s2ag_ids[i:i+chunk_size] for i in range(0, len(s2ag_ids), chunk_size)]
    for chunk_idx, chunk in enumerate(chunks):
        chunk_key = hash(tuple(sorted(chunk)))
        cache_file = cache_dir / f"batch_{chunk_key}.json"
        if cache_file.exists():
            cached = json.loads(cache_file.read_text())
            results.update(cached)
            continue
        print(f"  resolving batch {chunk_idx+1}/{len(chunks)} ({len(chunk)} IDs)...")
        try:
            headers = _make_headers()
            resp = requests.post(
                f"{S2AG_BASE}/paper/batch",
                params={"fields": BATCH_FIELDS},
                json={"ids": chunk},
                headers=headers,
                timeout=60,
            )
            if resp.status_code == 429:
                print("    rate-limited on batch; sleeping 60s")
                time.sleep(60)
                resp = requests.post(
                    f"{S2AG_BASE}/paper/batch",
                    params={"fields": BATCH_FIELDS},
                    json={"ids": chunk},
                    headers=headers,
                    timeout=60,
                )
            resp.raise_for_status()
            batch_result = resp.json()
            chunk_map: dict[str, dict | None] = {}
            for paper_data, s2ag_id in zip(batch_result, chunk):
                original_id = id_map.get(s2ag_id, s2ag_id)
                chunk_map[original_id] = paper_data  # None if not found
            cache_file.write_text(json.dumps(chunk_map))
            results.update(chunk_map)
            time.sleep(SLEEP_SECS)
        except requests.RequestException as exc:
            print(f"    batch resolution failed: {exc}")
            for s2ag_id in chunk:
                original_id = id_map.get(s2ag_id, s2ag_id)
                results[original_id] = None
    return results


def fetch_references(paper_id: str, cache_dir: Path) -> list[dict]:
    """Fetch outgoing references for a paper with local cache."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', paper_id)
    cache_file = cache_dir / f"refs_{safe_id}.json"
    url = f"{S2AG_BASE}/paper/{paper_id}/references"
    params = {"fields": REF_FIELDS, "limit": 1000}
    raw = _api_get(url, params, cache_file)
    if isinstance(raw, dict) and "data" in raw:
        return [r["citedPaper"] for r in raw["data"] if r.get("citedPaper")]
    if isinstance(raw, list):
        return raw
    return []


# ── Classification ────────────────────────────────────────────────────────────

def classify_paper(paper: dict, scheme: dict) -> str | None:
    """Classify a single S2AG paper into ML_NLP, HCI, or None."""
    if scheme.get("use_fos"):
        fos = set(paper.get("fieldsOfStudy") or [])
        if "Human-Computer Interaction" in fos:
            return "HCI"
        if fos & {"Computer Science", "Linguistics"}:
            venue = (paper.get("venue") or "").lower()
            if any(v in venue for v in scheme["hci"]):
                return "HCI"
            return "ML_NLP"
        # fall through to venue-string check
    venue = (paper.get("venue") or "").lower()
    if any(v in venue for v in scheme["hci"]):
        return "HCI"
    if any(v in venue for v in scheme["ml_nlp"]):
        return "ML_NLP"
    return None


def classify_all(resolved: dict[str, dict | None], scheme: dict) -> dict[str, str | None]:
    """Classify all resolved papers under a single scheme. Returns {paperId: group}."""
    groups: dict[str, str | None] = {}
    for paper_data in resolved.values():
        if paper_data and paper_data.get("paperId"):
            pid = paper_data["paperId"]
            groups[pid] = classify_paper(paper_data, scheme)
    return groups


# ── Graph Construction ────────────────────────────────────────────────────────

def build_graph(
    resolved: dict[str, dict | None],
    groups: dict[str, str | None],
    cache_dir: Path,
) -> tuple[nx.DiGraph, dict[tuple, int]]:
    """Build within-corpus directed citation graph and count cross-group edges."""
    corpus_ids = {p["paperId"] for p in resolved.values() if p and p.get("paperId")}
    G = nx.DiGraph()
    G.add_nodes_from(corpus_ids)
    edge_counts: dict[tuple, int] = defaultdict(int)

    total = len(corpus_ids)
    for idx, paper_id in enumerate(corpus_ids):
        if idx % 50 == 0:
            print(f"    fetching references {idx}/{total}...")
        refs = fetch_references(paper_id, cache_dir)
        src_group = groups.get(paper_id)
        for ref in refs:
            ref_id = ref.get("paperId")
            if ref_id and ref_id in corpus_ids:
                G.add_edge(paper_id, ref_id)
                tgt_group = groups.get(ref_id)
                if src_group and tgt_group:
                    edge_counts[(src_group, tgt_group)] += 1

    return G, edge_counts


# ── Gate Evaluation ───────────────────────────────────────────────────────────

def evaluate_gate(
    coverage: float,
    resolved_count: int,
    total_count: int,
    scheme_results: dict[str, dict],
) -> dict:
    """Evaluate H-E1 gate from coverage and per-scheme edge counts."""
    schemes_out = {}
    for scheme_name, ec in scheme_results.items():
        ml_ml = ec.get(("ML_NLP", "ML_NLP"), 0)
        ml_hci = ec.get(("ML_NLP", "HCI"), 0)
        hci_ml = ec.get(("HCI", "ML_NLP"), 0)
        hci_hci = ec.get(("HCI", "HCI"), 0)
        cross = ml_hci + hci_ml
        schemes_out[scheme_name] = {
            "ML_NLP_ML_NLP": ml_ml,
            "ML_NLP_HCI": ml_hci,
            "HCI_ML_NLP": hci_ml,
            "HCI_HCI": hci_hci,
            "cross_group_total": cross,
            "pass": coverage >= COVERAGE_GATE and cross >= CROSS_GROUP_GATE,
        }
    gate_pass = (
        coverage >= COVERAGE_GATE
        and any(s["cross_group_total"] >= CROSS_GROUP_GATE for s in schemes_out.values())
    )
    return {
        "coverage": coverage,
        "resolved": resolved_count,
        "total": total_count,
        "schemes": schemes_out,
        "gate_pass": gate_pass,
    }


# ── Visualization ─────────────────────────────────────────────────────────────

def plot_gate_metrics(coverage: float, scheme_results: dict, out: Path) -> None:
    """Figure 1: two-panel bar chart — coverage vs threshold; cross-group per scheme."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Panel 1: coverage
    ax1.bar(["Coverage"], [coverage], color="steelblue", label=f"{coverage:.1%}")
    ax1.axhline(COVERAGE_GATE, color="red", linestyle="--", label=f"Gate ({COVERAGE_GATE:.0%})")
    ax1.set_ylim(0, 1.05)
    ax1.set_ylabel("Fraction")
    ax1.set_title("Paper ID Coverage")
    ax1.legend()

    # Panel 2: cross-group edges per scheme
    scheme_names = list(scheme_results.keys())
    cross_counts = [scheme_results[s]["cross_group_total"] for s in scheme_names]
    colors = ["green" if c >= CROSS_GROUP_GATE else "salmon" for c in cross_counts]
    ax2.bar(scheme_names, cross_counts, color=colors)
    ax2.axhline(CROSS_GROUP_GATE, color="red", linestyle="--", label=f"Gate ({CROSS_GROUP_GATE})")
    ax2.set_ylabel("Edge Count")
    ax2.set_title("Cross-Group Edges (AI↔HCI)")
    ax2.legend()

    fig.tight_layout()
    fig.savefig(out / "fig1_gate_metrics.png", dpi=150)
    plt.close(fig)
    print(f"  saved fig1_gate_metrics.png")


def plot_dropout_by_venue(unresolved_ids: list[str], corpus_ids: list[str], out: Path) -> None:
    """Figure 2: bar chart of unresolved papers by inferred venue."""
    venue_counts: dict[str, int] = defaultdict(int)
    for pid in unresolved_ids:
        # Infer venue from ID prefix
        if pid.startswith("arXiv:"):
            venue_counts["arXiv (unresolved)"] += 1
        elif pid.startswith("10."):
            venue_counts["DOI (unresolved)"] += 1
        else:
            venue_counts["Unknown"] += 1
    venue_counts["arXiv (unresolved)"] = venue_counts.get("arXiv (unresolved)", 0)

    fig, ax = plt.subplots(figsize=(8, 4))
    if venue_counts:
        ax.bar(list(venue_counts.keys()), list(venue_counts.values()), color="coral")
    ax.set_xlabel("ID type")
    ax.set_ylabel("Count")
    ax.set_title(f"Unresolved Papers by ID Type ({len(unresolved_ids)} total)")
    fig.tight_layout()
    fig.savefig(out / "fig2_dropout_by_venue.png", dpi=150)
    plt.close(fig)
    print(f"  saved fig2_dropout_by_venue.png")


def plot_edge_heatmaps(scheme_results: dict, out: Path) -> None:
    """Figure 3: 2×2 edge-count heatmap per scheme (3 subplots)."""
    scheme_names = list(scheme_results.keys())
    fig, axes = plt.subplots(1, len(scheme_names), figsize=(5 * len(scheme_names), 4))
    if len(scheme_names) == 1:
        axes = [axes]
    labels = ["ML_NLP", "HCI"]
    for ax, sname in zip(axes, scheme_names):
        sr = scheme_results[sname]
        matrix = [
            [sr["ML_NLP_ML_NLP"], sr["ML_NLP_HCI"]],
            [sr["HCI_ML_NLP"], sr["HCI_HCI"]],
        ]
        im = ax.imshow(matrix, cmap="Blues")
        ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
        ax.set_xticklabels(labels); ax.set_yticklabels(labels)
        ax.set_xlabel("Target"); ax.set_ylabel("Source")
        ax.set_title(sname)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(matrix[i][j]), ha="center", va="center", color="black")
        fig.colorbar(im, ax=ax)
    fig.suptitle("Within-Corpus Citation Edge Counts")
    fig.tight_layout()
    fig.savefig(out / "fig3_edge_heatmaps.png", dpi=150)
    plt.close(fig)
    print(f"  saved fig3_edge_heatmaps.png")


def plot_venue_pie(groups: dict[str, str | None], out: Path) -> None:
    """Figure 4: pie chart ML_NLP / HCI / unclassified under scheme1."""
    counts: dict[str, int] = defaultdict(int)
    for g in groups.values():
        counts[g if g else "Unclassified"] += 1
    labels = list(counts.keys())
    sizes = list(counts.values())
    colors = {"ML_NLP": "steelblue", "HCI": "orange", "Unclassified": "lightgrey"}
    pie_colors = [colors.get(l, "lightgrey") for l in labels]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, colors=pie_colors, autopct="%1.1f%%", startangle=90)
    ax.set_title("Corpus Venue Groups (Scheme 1)")
    fig.tight_layout()
    fig.savefig(out / "fig4_venue_pie.png", dpi=150)
    plt.close(fig)
    print(f"  saved fig4_venue_pie.png")


# ── Entry Point ───────────────────────────────────────────────────────────────

def main(
    corpus_dir: str = "corpus",
    cache_dir: str = "cache/s2ag",
    data_dir: str = "data",
    figures_dir: str = "figures",
    results_dir: str = "results",
) -> dict:
    cache_path = Path(cache_dir)
    data_path = Path(data_dir)
    figures_path = Path(figures_dir)
    results_path = Path(results_dir)
    for d in (cache_path, data_path, figures_path, results_path):
        d.mkdir(parents=True, exist_ok=True)

    # Step 1: Clone corpus
    print("\n[1] Cloning corpus...")
    corpus_path = clone_corpus(corpus_dir)

    # Step 2: Extract paper IDs
    print("\n[2] Extracting paper IDs...")
    corpus_ids = extract_paper_ids(corpus_path)
    (data_path / "corpus_ids.json").write_text(json.dumps(corpus_ids, indent=2))
    print(f"  total unique IDs: {len(corpus_ids)}")

    # Step 3: Resolve via S2AG
    print("\n[3] Resolving paper IDs via S2AG...")
    resolved = resolve_papers(corpus_ids, cache_path)
    valid = {k: v for k, v in resolved.items() if v and v.get("paperId")}
    unresolved = [k for k, v in resolved.items() if not (v and v.get("paperId"))]
    coverage = len(valid) / len(corpus_ids) if corpus_ids else 0.0
    print(f"  resolved: {len(valid)}/{len(corpus_ids)} ({coverage:.1%})")
    (data_path / "resolved_papers.json").write_text(json.dumps(resolved, indent=2))

    # Step 4: Classify + build graph per scheme
    print("\n[4] Classifying papers and building citation graphs...")
    scheme_results_ec: dict[str, dict] = {}
    scheme_groups: dict[str, dict] = {}
    for scheme_name, scheme in SCHEMES.items():
        print(f"  scheme: {scheme_name}")
        groups = classify_all(resolved, scheme)
        scheme_groups[scheme_name] = groups
        classified = sum(1 for g in groups.values() if g)
        print(f"    classified: {classified}/{len(groups)}")
        (data_path / f"paper_groups_{scheme_name}.json").write_text(json.dumps(groups, indent=2))

        G, edge_counts = build_graph(resolved, groups, cache_path)
        # Convert tuple keys to strings for JSON
        ec_serializable = {f"{k[0]}__{k[1]}": v for k, v in edge_counts.items()}
        (data_path / f"edge_counts_{scheme_name}.json").write_text(json.dumps(ec_serializable, indent=2))
        scheme_results_ec[scheme_name] = dict(edge_counts)

    # Step 5: Gate evaluation
    print("\n[5] Evaluating H-E1 gate...")
    gate_result = evaluate_gate(coverage, len(valid), len(corpus_ids), scheme_results_ec)
    (results_path / "h_e1_gate_result.json").write_text(json.dumps(gate_result, indent=2))
    print(f"  coverage: {coverage:.1%} (gate: ≥{COVERAGE_GATE:.0%})")
    for sname, sr in gate_result["schemes"].items():
        print(f"  {sname}: cross_group={sr['cross_group_total']} (gate: ≥{CROSS_GROUP_GATE}) → {'PASS' if sr['pass'] else 'FAIL'}")
    print(f"  H-E1 gate_pass: {gate_result['gate_pass']}")

    # Step 6: Figures
    print("\n[6] Generating figures...")
    plot_gate_metrics(coverage, gate_result["schemes"], figures_path)
    plot_dropout_by_venue(unresolved, corpus_ids, figures_path)
    plot_edge_heatmaps(gate_result["schemes"], figures_path)
    # Use scheme1 groups for pie chart
    plot_venue_pie(scheme_groups.get("scheme1", {}), figures_path)

    print("\n✅ H-E1 pipeline complete.")
    return gate_result


if __name__ == "__main__":
    import sys
    import os
    # Allow running from any directory by switching to code folder
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    result = main()
    print(f"\nGate result: {'PASS' if result['gate_pass'] else 'FAIL'}")
    sys.exit(0 if result["gate_pass"] else 1)
