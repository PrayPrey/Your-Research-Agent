#!/usr/bin/env python3
"""
Phase 2A Paper Preparation Script 

"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

import requests
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "openai/gpt-5.2"
DEFAULT_OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"


# ═══════════════════════════════════════════════════════════════
# PAPER DOWNLOAD
# ═══════════════════════════════════════════════════════════════

def download_from_semantic_scholar(paper_id: str, output_path: Path) -> Optional[Path]:
    """
    Download paper PDF from Semantic Scholar Open Access.

    Args:
        paper_id: Semantic Scholar paper ID
        output_path: Directory to save PDF

    Returns:
        Path to downloaded PDF or None if not available
    """
    api_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    params = {"fields": "openAccessPdf,title"}

    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data.get("openAccessPdf"):
            logger.warning(f"No Open Access PDF for paper: {paper_id}")
            return None

        pdf_url = data["openAccessPdf"]["url"]
        title = data.get("title", paper_id)

        # Download PDF
        pdf_response = requests.get(pdf_url, timeout=60)
        pdf_response.raise_for_status()

        # Save PDF
        safe_filename = re.sub(r'[^\w\-_]', '_', paper_id)[:50]
        pdf_path = output_path / f"{safe_filename}.pdf"

        with open(pdf_path, 'wb') as f:
            f.write(pdf_response.content)

        logger.info(f"Downloaded: {title[:50]}... -> {pdf_path.name}")
        return pdf_path

    except requests.RequestException as e:
        logger.error(f"Failed to download from Semantic Scholar: {paper_id} - {e}")
        return None


def download_from_arxiv(arxiv_id: str, output_path: Path) -> Optional[Path]:
    """
    Download paper PDF from arXiv.

    Args:
        arxiv_id: arXiv paper ID (e.g., "2301.00001" or "arxiv:2301.00001")
        output_path: Directory to save PDF

    Returns:
        Path to downloaded PDF or None if failed
    """
    # Clean up arXiv ID
    arxiv_id = arxiv_id.lower().replace("arxiv:", "").strip()

    # arXiv PDF URL format
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    try:
        response = requests.get(pdf_url, timeout=60)
        response.raise_for_status()

        # Save PDF
        safe_filename = re.sub(r'[^\w\-_]', '_', arxiv_id)
        pdf_path = output_path / f"arxiv_{safe_filename}.pdf"

        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Downloaded from arXiv: {arxiv_id} -> {pdf_path.name}")
        return pdf_path

    except requests.RequestException as e:
        logger.error(f"Failed to download from arXiv: {arxiv_id} - {e}")
        return None


def download_paper(paper_info: dict, output_path: Path) -> Optional[Path]:
    """
    Download paper from appropriate source based on paper info.

    Args:
        paper_info: Dict with 'id', 'source', and optionally 'url'
        output_path: Directory to save PDF

    Returns:
        Path to downloaded PDF or None
    """
    paper_id = paper_info.get("id", "")
    source = paper_info.get("source", "").lower()
    url = paper_info.get("url", "")

    # Determine source and download
    if source == "arxiv" or "arxiv" in paper_id.lower():
        return download_from_arxiv(paper_id, output_path)
    elif source == "semantic_scholar" or source == "openAccessPdf":
        return download_from_semantic_scholar(paper_id, output_path)
    elif url:
        # Try to infer source from URL
        if "arxiv.org" in url:
            arxiv_id = url.split("/")[-1].replace(".pdf", "")
            return download_from_arxiv(arxiv_id, output_path)
        else:
            logger.warning(f"Unknown source for paper: {paper_id}")
            return None
    else:
        # Try Semantic Scholar as default
        return download_from_semantic_scholar(paper_id, output_path)


# ═══════════════════════════════════════════════════════════════
# PDF TO MARKDOWN CONVERSION
# ═══════════════════════════════════════════════════════════════

def convert_pdf_to_markdown(pdf_path: Path) -> Optional[str]:
    """
    Convert PDF to Markdown using Microsoft MarkItDown.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Markdown content as string or None if failed
    """
    try:
        from markitdown import MarkItDown

        md = MarkItDown()
        result = md.convert(str(pdf_path))

        if result and result.text_content:
            logger.info(f"Converted to MD: {pdf_path.name}")
            return result.text_content
        else:
            logger.warning(f"Empty conversion result for: {pdf_path.name}")
            return None

    except ImportError:
        logger.error("MarkItDown not installed. Run: pip install markitdown")
        return None
    except Exception as e:
        logger.error(f"Failed to convert PDF: {pdf_path.name} - {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# REFERENCES EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_before_references(md_content: str) -> str:
    """
    Extract content before the References section.

    Args:
        md_content: Full markdown content

    Returns:
        Content up to (but not including) References section
    """
    # Patterns for References section headers
    patterns = [
        # Markdown headings
        r'(?m)^\s*#{1,3}\s*References?\s*$',
        r'(?m)^\s*#{1,3}\s*Bibliography\s*$',
        '(?m)^\\s*#{1,3}\\s*\\uCC38\\uACE0\\s*\\uBB38\\uD5CC\\s*$',

        # Bold headings
        r'(?m)^\s*\*\*References?\*\*\s*$',
        r'(?m)^\s*\*\*Bibliography\*\*\s*$',

        # Underline-style heading
        r'(?m)^\s*References?\s*\n\s*[-=]{3,}\s*$',

        # Numbered heading (optional)
        r'(?m)^\s*\d{1,2}\.\s*References?\s*$',

        # All-caps heading
        r'(?m)^\s*REFERENCES\s*$',
    ]

    earliest_match = None
    earliest_pos = len(md_content)

    for pattern in patterns:
        match = re.search(pattern, md_content, re.IGNORECASE)
        if match and match.start() < earliest_pos:
            earliest_match = match
            earliest_pos = match.start()

    if earliest_match:
        content = md_content[:earliest_pos].strip()
        logger.info(f"Extracted content before References (removed {len(md_content) - len(content)} chars)")
        return content
    else:
        logger.warning("References section not found, returning full content")
        return md_content


def add_metadata_header(md_content: str, paper_info: dict) -> str:
    """
    Add metadata header to the markdown content.

    Args:
        md_content: Markdown content
        paper_info: Paper metadata

    Returns:
        Markdown with metadata header
    """
    header = f"""---
paper_id: {paper_info.get('id', 'unknown')}
source: {paper_info.get('source', 'unknown')}
title: {paper_info.get('title', 'Unknown Title')}
converted_at: {datetime.now().isoformat()}
note: "Content extracted before References section"
---

"""
    return header + md_content


# ═══════════════════════════════════════════════════════════════
# LLM-POWERED PAPER SUMMARIZATION (v8.6.0)
# ═══════════════════════════════════════════════════════════════

def find_project_root() -> Optional[Path]:
    """Find the repository root by locating the Claude hook config."""
    candidates = [Path.cwd(), *Path(__file__).resolve().parents]
    for candidate in candidates:
        config_path = candidate / ".claude" / "hooks" / "auto_responder_config.yaml"
        if config_path.exists():
            return candidate
    return None


def load_env_files(project_root: Optional[Path]) -> None:
    """Load environment variables from common .env locations."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    candidates: List[Path] = [Path.cwd() / ".env"]
    if project_root is not None:
        candidates.append(project_root / ".env")

    for parent in Path(__file__).resolve().parents:
        candidates.append(parent / ".env")

    seen = set()
    for env_candidate in candidates:
        env_candidate = env_candidate.resolve()
        if env_candidate in seen:
            continue
        seen.add(env_candidate)
        if env_candidate.exists():
            load_dotenv(env_candidate)
            logger.info(f"Loaded .env from: {env_candidate}")
            break


def load_openrouter_settings(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Load OpenRouter settings from .claude/hooks/auto_responder_config.yaml."""
    settings: Dict[str, Any] = {
        "provider": "openrouter",
        "base_url": OPENROUTER_BASE_URL,
        "model": DEFAULT_OPENROUTER_MODEL,
        "api_key_env": DEFAULT_OPENROUTER_API_KEY_ENV,
        "timeout_seconds": 240,
        "max_tokens": 4000,
        "config_path": None,
    }

    root = project_root or find_project_root()
    if root is None:
        logger.warning(
            "auto_responder_config.yaml not found; using default OpenRouter settings"
        )
        return settings

    config_path = root / ".claude" / "hooks" / "auto_responder_config.yaml"
    settings["config_path"] = str(config_path)

    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    except Exception as e:
        logger.warning(f"Failed to read OpenRouter config {config_path}: {e}")
        return settings

    openrouter = cfg.get("openrouter", {})
    if not isinstance(openrouter, dict):
        return settings

    settings["model"] = openrouter.get("model") or settings["model"]
    settings["api_key_env"] = openrouter.get("api_key_env") or settings["api_key_env"]
    settings["timeout_seconds"] = int(
        openrouter.get("timeout_seconds") or settings["timeout_seconds"]
    )
    settings["max_tokens"] = int(openrouter.get("max_tokens") or settings["max_tokens"])
    return settings


def normalize_openrouter_model(model: Optional[str]) -> str:
    """Convert common OpenAI model names to OpenRouter model IDs."""
    selected = (model or DEFAULT_OPENROUTER_MODEL).strip()
    if "/" not in selected and selected.startswith("gpt-"):
        return f"openai/{selected}"
    return selected


SUMMARY_SYSTEM_PROMPT = """You are an expert academic paper summarizer for deep learning research.
Your task is to produce a structured, concise summary of a paper that will be used during a research hypothesis discussion.

Requirements:
- Preserve technical precision (exact method names, metrics, numbers)
- Keep mathematical notation and key equations
- Focus on WHAT they did and WHY, not filler text
- Each section summary should be self-contained and useful independently
- Methodology and Experiments sections should be DETAILED (see word counts below)
- Total output should be 2500-3500 tokens

Output format (strict markdown):

# {Paper Title}

## Key Metadata
- **Authors:** [First Author] et al.
- **Year:** [Year]
- **Venue:** [Conference/Journal if detectable]
- **Core Contribution:** [1 sentence]

## Section Summaries

### Abstract
[Copy the abstract verbatim — it's already concise]

### Introduction & Motivation
[3-5 sentences: problem statement, why it matters, gap addressed]

### Methodology
[DETAILED — 200-300 words. Include ALL of the following:]
- Core algorithm/technique name and how it works step-by-step
- Model architecture details (layers, dimensions, attention mechanisms, etc.)
- Key hyperparameters and their values (learning rate, batch size, epochs, etc.)
- Training procedure (optimizer, scheduler, loss functions with formulas)
- Input/output format and data preprocessing pipeline
- Any novel components and how they differ from prior work
[Preserve ALL key equations in LaTeX notation]

### Experiments & Results
[DETAILED — 200-300 words. Include ALL of the following:]
- Dataset names, sizes, and train/val/test split ratios
- Evaluation metrics used (exact names: BLEU, ROUGE-L, F1, accuracy, etc.)
- Baseline methods compared against (with citations)
- Main result numbers in a compact table
- Ablation study findings (which components contribute most)
- Statistical significance or confidence intervals if reported
- Computational cost (GPU hours, inference speed) if mentioned

### Discussion & Conclusion
[2-3 sentences: main takeaways, limitations acknowledged, future directions]

## Key Contributions
- [Contribution 1]
- [Contribution 2]
- [Contribution 3]

## Potential Relevance
[2-3 sentences: what aspects of this paper might be useful for hypothesis development — methods, findings, baselines, or negative results]
"""


def _get_openrouter_client(settings: Dict[str, Any]):
    """Initialize an OpenAI-compatible client for OpenRouter."""
    try:
        from openai import OpenAI
    except ImportError:
        logger.error("openai package not installed. Run: pip install openai")
        return None

    api_key_env = settings.get("api_key_env", DEFAULT_OPENROUTER_API_KEY_ENV)
    api_key = os.environ.get(api_key_env, "").strip()
    if not api_key:
        logger.error(f"{api_key_env} not set in environment")
        return None

    return OpenAI(
        api_key=api_key,
        base_url=settings.get("base_url", OPENROUTER_BASE_URL),
        timeout=settings.get("timeout_seconds", 240),
    )


def _chunk_content(content: str, max_chars: int = 80000) -> str:
    """Truncate content to fit within LLM context window.

    GPT-5.2 has a large context, but we still cap input to avoid
    excessive cost and latency. 80k chars ≈ 20k tokens.
    """
    if len(content) <= max_chars:
        return content

    # Keep first 60% and last 20% to preserve intro + conclusion
    head = int(max_chars * 0.6)
    tail = int(max_chars * 0.2)
    middle_note = (
        "\n\n[... MIDDLE SECTION TRUNCATED FOR SUMMARIZATION ...]\n\n"
    )
    return content[:head] + middle_note + content[-tail:]


FALLBACK_MODELS = ["openai/gpt-5-mini", "openai/gpt-4.1-mini", "openai/gpt-4.1-nano"]


def summarize_single_paper(
    md_path: Path,
    output_dir: Path,
    client,
    model: str = DEFAULT_OPENROUTER_MODEL,
    max_tokens: int = 4000,
    max_retries: int = 2,
) -> Optional[Path]:
    """Summarize a single paper MD file using OpenAI GPT.

    Args:
        md_path: Path to the full paper markdown file
        output_dir: Directory to save the summary
        client: OpenAI client instance
        model: Model to use for summarization
        max_retries: Number of retries on API failure

    Returns:
        Path to the generated summary file, or None on failure
    """
    paper_stem = md_path.stem
    summary_path = output_dir / f"{paper_stem}_summary.md"
    model = normalize_openrouter_model(model)

    # Skip if summary already exists and is recent
    if summary_path.exists():
        logger.info(f"Summary already exists, skipping: {summary_path.name}")
        return summary_path

    # Read paper content
    try:
        content = md_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Cannot read {md_path}: {e}")
        return None

    if len(content.strip()) < 500:
        logger.warning(f"Paper too short to summarize ({len(content)} chars): {md_path.name}")
        return None

    # Truncate if needed
    content = _chunk_content(content)

    # Build model fallback list: primary model first, then fallbacks (deduplicated)
    models_to_try = [model]
    for fb in FALLBACK_MODELS:
        if fb not in models_to_try:
            models_to_try.append(fb)

    # Try each model with retries
    for current_model in models_to_try:
        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    f"Summarizing {md_path.name} ({len(content)} chars) "
                    f"with {current_model} (attempt {attempt + 1}/{max_retries + 1})..."
                )

                response = client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": (
                                f"Summarize this paper:\n\n{content}"
                            ),
                        },
                    ],
                    max_tokens=max_tokens,
                )

                # Safely extract content (handle None)
                raw_content = response.choices[0].message.content
                summary_text = raw_content.strip() if raw_content else ""

                # Log response metadata for debugging
                finish_reason = response.choices[0].finish_reason
                usage = response.usage
                refusal = getattr(response.choices[0].message, "refusal", None)

                if len(summary_text) < 200:
                    logger.warning(
                        f"Summary suspiciously short ({len(summary_text)} chars) — "
                        f"finish_reason={finish_reason}, "
                        f"refusal={refusal}, "
                        f"prompt_tokens={usage.prompt_tokens if usage else '?'}, "
                        f"completion_tokens={usage.completion_tokens if usage else '?'}, "
                        f"model={current_model}"
                    )
                    if attempt < max_retries:
                        wait = 2 ** (attempt + 1)
                        logger.info(f"Retrying in {wait}s with same model...")
                        time.sleep(wait)
                    continue

                # Add generation metadata header
                actual_model = current_model
                header = f"""---
source_paper: "{md_path.name}"
generated_at: "{datetime.now().isoformat()}"
model: "{actual_model}"
summary_chars: {len(summary_text)}
---

"""
                summary_path.write_text(header + summary_text, encoding="utf-8")
                logger.info(
                    f"Summary saved: {summary_path.name} ({len(summary_text)} chars, model={actual_model})"
                )
                return summary_path

            except Exception as e:
                logger.error(f"API call failed (model={current_model}, attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    wait = 2 ** (attempt + 1)
                    logger.info(f"Retrying in {wait}s...")
                    time.sleep(wait)

        logger.warning(f"All {max_retries + 1} attempts failed with {current_model}, trying next model...")

    logger.error(f"Failed to summarize after trying all models {models_to_try}: {md_path.name}")
    return None


def summarize_papers(
    papers_dir: Path,
    summaries_dir: Path,
    model: Optional[str] = None,
) -> Dict:
    """Summarize all paper MD files in a directory.

    Args:
        papers_dir: Directory containing paper .md files
        summaries_dir: Directory to save summaries
        model: Optional OpenRouter model override. Defaults to auto_responder_config.yaml.

    Returns:
        Summary result dict
    """
    project_root = find_project_root()
    settings = load_openrouter_settings(project_root)
    selected_model = normalize_openrouter_model(model or settings.get("model"))

    # Find paper MD files (exclude preparation_summary.json and summary files)
    md_files = [
        f for f in sorted(papers_dir.glob("*.md"))
        if not f.name.endswith("_summary.md")
    ]

    if not md_files:
        logger.warning(f"No MD files found in {papers_dir}")
        return {
            "status": "no_papers",
            "total": 0,
            "success": 0,
            "failed": 0,
            "provider": "openrouter",
            "model": selected_model,
            "summaries_dir": str(summaries_dir),
            "results": [],
        }

    summaries_dir.mkdir(parents=True, exist_ok=True)

    client = _get_openrouter_client(settings)
    if not client:
        summary_result = {
            "status": "error",
            "error": "OpenRouter client initialization failed",
            "total": len(md_files),
            "success": 0,
            "failed": len(md_files),
            "provider": "openrouter",
            "model": selected_model,
            "api_key_env": settings.get("api_key_env", DEFAULT_OPENROUTER_API_KEY_ENV),
            "summaries_dir": str(summaries_dir),
            "results": [
                {
                    "paper": md_file.name,
                    "summary": None,
                    "status": "failed",
                    "error": "OpenRouter client initialization failed",
                }
                for md_file in md_files
            ],
            "summarized_at": datetime.now().isoformat(),
        }
        report_path = summaries_dir / "summarization_report.json"
        with open(report_path, "w") as f:
            json.dump(summary_result, f, indent=2)
        return summary_result

    logger.info(f"Found {len(md_files)} papers to summarize")
    logger.info(
        "Using OpenRouter for paper summarization: "
        f"model={selected_model}, api_key_env={settings.get('api_key_env')}"
    )

    results = []
    success_count = 0

    for md_file in md_files:
        summary_path = summarize_single_paper(
            md_file,
            summaries_dir,
            client,
            model=selected_model,
            max_tokens=settings.get("max_tokens", 3000),
        )
        result = {
            "paper": md_file.name,
            "summary": str(summary_path) if summary_path else None,
            "status": "success" if summary_path else "failed",
        }
        results.append(result)
        if summary_path:
            success_count += 1

    summary_result = {
        "status": "completed",
        "total": len(md_files),
        "success": success_count,
        "failed": len(md_files) - success_count,
        "provider": "openrouter",
        "model": selected_model,
        "summaries_dir": str(summaries_dir),
        "results": results,
        "summarized_at": datetime.now().isoformat(),
    }

    # Save summary report
    report_path = summaries_dir / "summarization_report.json"
    with open(report_path, "w") as f:
        json.dump(summary_result, f, indent=2)

    logger.info(
        f"Summarization complete: {success_count}/{len(md_files)} successful"
    )
    return summary_result


# ═══════════════════════════════════════════════════════════════
# MAIN PROCESSING
# ═══════════════════════════════════════════════════════════════

def process_paper(paper_info: dict, output_dir: Path) -> dict:
    """
    Process a single paper: download, convert, extract.

    Args:
        paper_info: Paper metadata dict
        output_dir: Output directory

    Returns:
        Result dict with status and paths
    """
    paper_id = paper_info.get("id", "unknown")
    result = {
        "paper_id": paper_id,
        "status": "pending",
        "pdf_path": None,
        "md_path": None,
        "error": None
    }

    try:
        # Step 1: Download PDF
        pdf_path = download_paper(paper_info, output_dir)
        if not pdf_path:
            result["status"] = "download_failed"
            result["error"] = "Could not download PDF"
            return result
        result["pdf_path"] = str(pdf_path)

        # Step 2: Convert to Markdown
        md_content = convert_pdf_to_markdown(pdf_path)
        if not md_content:
            result["status"] = "conversion_failed"
            result["error"] = "Could not convert PDF to Markdown"
            return result

        # Step 3: Extract before References
        extracted_content = extract_before_references(md_content)

        # Step 4: Add metadata header
        final_content = add_metadata_header(extracted_content, paper_info)

        # Step 5: Save Markdown
        md_path = pdf_path.with_suffix('.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        result["md_path"] = str(md_path)
        result["status"] = "success"
        logger.info(f"Successfully processed: {paper_id}")

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Error processing {paper_id}: {e}")

    return result


def process_papers(config: dict, output_dir: Path) -> dict:
    """
    Process all papers from config.

    Args:
        config: Configuration with paper list
        output_dir: Output directory

    Returns:
        Summary dict with all results
    """
    papers = config.get("papers", [])

    if not papers:
        logger.warning("No papers to process")
        return {
            "status": "no_papers",
            "total": 0,
            "success": 0,
            "failed": 0,
            "output_dir": str(output_dir),
            "results": [],
        }

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    success_count = 0

    for paper_info in papers:
        result = process_paper(paper_info, output_dir)
        results.append(result)
        if result["status"] == "success":
            success_count += 1

    summary = {
        "status": "completed",
        "total": len(papers),
        "success": success_count,
        "failed": len(papers) - success_count,
        "output_dir": str(output_dir),
        "results": results,
        "processed_at": datetime.now().isoformat()
    }

    # Save summary
    summary_path = output_dir / "preparation_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Processing complete: {success_count}/{len(papers)} successful")
    return summary


# ═══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Prepare papers for Phase 2A: Download, convert, and summarize"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to config YAML with paper list (required for download mode)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory for papers (required for download mode)"
    )
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Enable LLM-powered paper summarization"
    )
    parser.add_argument(
        "--papers-dir",
        type=str,
        help="Papers directory for standalone summarization (defaults to --output)"
    )
    parser.add_argument(
        "--summaries-dir",
        type=str,
        help="Output directory for summaries (defaults to {papers-dir}/../paper_summaries)"
    )
    parser.add_argument(
        "--summary-model",
        type=str,
        default=None,
        help=(
            "OpenRouter model override for summarization. "
            "Defaults to .claude/hooks/auto_responder_config.yaml openrouter.model."
        )
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    project_root = find_project_root()
    load_env_files(project_root)

    # Standalone summarize mode (no download needed)
    standalone_summarize = args.summarize and not args.config

    if standalone_summarize:
        if not args.papers_dir:
            parser.error("--papers-dir is required for standalone summarization")

        papers_dir = Path(args.papers_dir)
        summaries_dir = (
            Path(args.summaries_dir) if args.summaries_dir
            else papers_dir.parent / "paper_summaries"
        )

        result = summarize_papers(papers_dir, summaries_dir, model=args.summary_model)

        print(f"\n{'='*60}")
        print("Paper Summarization Report")
        print(f"{'='*60}")
        print(f"Total papers:  {result['total']}")
        print(f"Summarized:    {result['success']}")
        print(f"Failed:        {result.get('failed', 0)}")
        print(f"Provider:      {result.get('provider', 'N/A')}")
        print(f"Model:         {result.get('model', 'N/A')}")
        if result.get("error"):
            print(f"Error:         {result['error']}")
        print(f"Summaries dir: {result.get('summaries_dir', 'N/A')}")
        print(f"{'='*60}\n")

        sys.exit(0 if result.get('failed', 0) == 0 else 1)

    # Download + convert mode (original behavior)
    if not args.config or not args.output:
        parser.error("--config and --output are required for download mode")

    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    output_dir = Path(args.output)
    summary = process_papers(config, output_dir)

    print(f"\n{'='*60}")
    print("Paper Preparation Summary")
    print(f"{'='*60}")
    print(f"Total papers: {summary['total']}")
    print(f"Successful:   {summary['success']}")
    print(f"Failed:       {summary['failed']}")
    print(f"Output dir:   {summary['output_dir']}")
    print(f"{'='*60}\n")

    # If --summarize flag is also set, run summarization after download
    if args.summarize and summary['success'] > 0:
        summaries_dir = (
            Path(args.summaries_dir) if args.summaries_dir
            else output_dir.parent / "paper_summaries"
        )
        sum_result = summarize_papers(output_dir, summaries_dir, model=args.summary_model)

        print(f"\n{'='*60}")
        print("Paper Summarization Report")
        print(f"{'='*60}")
        print(f"Summarized:    {sum_result['success']}/{sum_result['total']}")
        print(f"Failed:        {sum_result.get('failed', 0)}")
        print(f"Provider:      {sum_result.get('provider', 'N/A')}")
        print(f"Model:         {sum_result.get('model', 'N/A')}")
        if sum_result.get("error"):
            print(f"Error:         {sum_result['error']}")
        print(f"Summaries dir: {sum_result.get('summaries_dir', 'N/A')}")
        print(f"{'='*60}\n")

    if summary['failed'] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
