#!/usr/bin/env python3
"""
Phase 2A Discussion Orchestrator (Standalone Script)

Standalone script for Phase 2A hypothesis discussion orchestration.
Called via Bash from step-01-discussion.md's Self-Contained Loop.

Replaces the Hook-based phase2a_orchestrator.py with a direct CLI tool:
1. Reads discussion_log.md
2. Calls external LLM (OpenRouter) for persona selection + convergence check
3. Outputs JSON to stdout for Claude to parse

Usage:
    python orchestrate_exchange.py \
        --discussion-log <path/to/discussion_log.md> \
        --config <path/to/phase2a_config.yaml> \
        --personas <path/to/personas.yaml> \
        --research-folder <path/to/research_folder>

Output (JSON to stdout):
    Not converged (LLM wrote exchange):
    {"converged": false, "exchange_number": 4,
     "llm_exchange": "🔬 **Prof. Vera** (...):\n\n[full response]",
     "llm_persona": {"name": "Prof. Vera", "icon": "🔬"},
     "claude_persona": {"name": "Dr. Nova", "icon": "🔭"}}

    Converged:
    {"converged": true, "exchange_number": 7, "summary": "Key achievements: ..."}

    Fallback (LLM failed, Claude writes both):
    {"converged": false, "exchange_number": N, "llm_exchange": null,
     "llm_persona": {...}, "claude_persona": {...}, "fallback": true}

Must be run in YouRA virtual environment (conda activate YouRA).

Author: Anonymous
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Optional, Tuple, Dict, Any, List

# Load .env file for API keys
try:
    from dotenv import load_dotenv
    # Try project root (multiple possible locations)
    for candidate in [
        Path.cwd() / ".env",
        Path(__file__).parent.parent.parent.parent.parent.parent.parent / ".env",
    ]:
        if candidate.exists():
            load_dotenv(candidate)
            break
except ImportError:
    pass

import requests

try:
    import yaml
except ImportError:
    print(json.dumps({"error": "pyyaml not installed. Run: pip install pyyaml"}), file=sys.stdout)
    sys.exit(1)


# ============================================================
# Logging (stderr only — stdout reserved for JSON output)
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


# ============================================================
# Configuration Loading
# ============================================================
def get_default_config() -> Dict[str, Any]:
    """Return default configuration."""
    return {
        "enabled": True,
        "openrouter": {
            "enabled": True,
            "model": "openai/gpt-5.2-chat",
            "api_key_env": "OPENROUTER_API_KEY",
            "timeout_seconds": 60,
            "max_tokens": 1000,
        },
        "discussion": {
            "min_exchanges": 15,
            "target_exchanges": 35,
            "max_exchanges": 50,
            "instruction_mode": "topic",
            "personas_per_exchange": 1,
            "turn_mode": "intelligent",
        },
        "papers": {
            "enabled": True,
            "folder_pattern": "papers/*.md",
            "suggest_on": ["methodology", "mechanism", "evidence", "comparison"],
        },
        "detection": {
            "discussion_log": "discussion_log.md",
            "completion_marker": "## Final Assessments",
        },
        "debug": {
            "verbose": True,
            "log_llm_interactions": False,
        },
    }


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return get_default_config()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config if config else get_default_config()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return get_default_config()


# ============================================================
# Persona Loading
# ============================================================
def load_personas(personas_path: Path) -> Dict[str, Any]:
    """Load personas from personas.yaml."""
    if not personas_path.exists():
        logger.warning(f"personas.yaml not found: {personas_path}, using fallback")
        return get_fallback_personas()

    try:
        with open(personas_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        logger.info(f"Loaded personas from: {personas_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading personas: {e}")
        return get_fallback_personas()


def get_fallback_personas() -> Dict[str, Any]:
    """Fallback personas if YAML cannot be loaded."""
    return {
        "perspective": [
            {"icon": "\U0001f52d", "name": "Dr. Nova", "title": "Creative Novelty Explorer"},
            {"icon": "\U0001f52c", "name": "Prof. Vera", "title": "Rigorous Validation Architect"},
            {"icon": "\U0001f3af", "name": "Dr. Sage", "title": "Research Impact Evaluator"},
            {"icon": "\u2699\ufe0f", "name": "Prof. Pax", "title": "Feasibility & Reality Checker"},
        ],
        "refinement": [
            {"icon": "\U0001f6e1\ufe0f", "name": "Dr. Ally", "title": "Hypothesis Strengthening Champion"},
            {"icon": "\U0001f50d", "name": "Prof. Rex", "title": "Hypothesis Stress-Test Master"},
        ],
        "convergence": {
            "min_exchanges": 13,
            "max_exchanges": 50,
            "criteria": [
                {"id": "SPECIFIC", "description": "Clear core claim stated"},
                {"id": "MECHANISM", "description": "How it works explained"},
                {"id": "PREDICTIONS", "description": "2-3 testable predictions with criteria"},
                {"id": "NOVELTY", "description": "What's new articulated"},
                {"id": "FEASIBILITY", "description": "Implementation realistic"},
                {"id": "OBJECTIONS", "description": "Major criticisms addressed"},
            ],
        },
    }


# ============================================================
# Persona Helpers
# ============================================================
def get_all_personas_flat(personas_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get flat list of all personas."""
    result = []
    for p in personas_data.get("perspective", []):
        result.append(p)
    for p in personas_data.get("refinement", []):
        result.append(p)
    return result


def find_persona_by_name(personas_data: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
    """Find persona by name (case-insensitive, partial match)."""
    name_lower = name.lower().strip()
    for p in get_all_personas_flat(personas_data):
        if p["name"].lower() == name_lower:
            return p
    for p in get_all_personas_flat(personas_data):
        if name_lower in p["name"].lower() or p["name"].lower() in name_lower:
            return p
    return None


def build_persona_roster(personas_data: Dict[str, Any]) -> str:
    """Build markdown table from loaded personas."""
    lines = ["| Icon | Name | Role |", "|------|------|------|"]
    for p in personas_data.get("perspective", []):
        lines.append(f"| {p['icon']} | {p['name']} | {p['title']} |")
    for p in personas_data.get("refinement", []):
        lines.append(f"| {p['icon']} | {p['name']} | {p['title']} |")
    return "\n".join(lines)


def build_persona_detail(persona: Dict[str, Any]) -> str:
    """Build detailed persona description for LLM 2 instruction prompt."""
    lines = [
        f"## {persona['icon']} {persona['name']} — {persona['title']}",
        f"**Role:** {persona.get('role', '')}",
        f"**Stage:** {persona.get('stage', '')}",
        "",
        "### Identity",
        persona.get("identity", "").strip(),
        "",
        "### Communication Style",
        persona.get("communication_style", "").strip(),
        "",
        "### Principles",
    ]
    for principle in persona.get("principles", []):
        lines.append(f"- {principle}")
    lines.append("")
    lines.append("### Response Focus")
    for focus in persona.get("response_focus", []):
        lines.append(f"- {focus}")
    lines.append("")
    lines.append("### Key Questions")
    for q in persona.get("key_questions", []):
        lines.append(f"- {q}")
    if persona.get("critical_note"):
        lines.append("")
        lines.append("### Critical Note")
        lines.append(persona["critical_note"].strip())
    return "\n".join(lines)


def get_all_icons(personas_data: Dict[str, Any]) -> List[str]:
    """Get list of all persona icons for speaker detection."""
    icons = []
    for p in personas_data.get("perspective", []):
        icons.append(p["icon"])
    for p in personas_data.get("refinement", []):
        icons.append(p["icon"])
    return icons


def build_convergence_checklist(personas_data: Dict[str, Any]) -> str:
    """Build convergence criteria checklist."""
    convergence = personas_data.get("convergence", {})
    criteria = convergence.get("criteria", [])
    if not criteria:
        return (
            "- [ ] SPECIFIC: Clear core claim stated?\n"
            "- [ ] MECHANISM: How it works explained?\n"
            "- [ ] PREDICTIONS: 2-3 testable predictions with criteria?\n"
            "- [ ] NOVELTY: What's new articulated?\n"
            "- [ ] FEASIBILITY: Technical/theoretical feasibility established?\n"
            "- [ ] OBJECTIONS: Major criticisms addressed?"
        )
    lines = []
    for c in criteria:
        desc = c.get("description", "")
        lines.append(f"- [ ] {c['id']}: {desc}?")
        if "full_description" in c and c["id"] == "FEASIBILITY":
            full_desc = c["full_description"].strip()
            lines.append(f"      ({full_desc.split(chr(10))[0]})")
    return "\n".join(lines)


def get_next_round_robin_persona(exchange_count: int, personas_data: Dict[str, Any]) -> Dict[str, str]:
    """Get next persona in round-robin order."""
    all_personas = []
    for p in personas_data.get("perspective", []):
        all_personas.append({"name": p["name"], "icon": p["icon"]})
    for p in personas_data.get("refinement", []):
        all_personas.append({"name": p["name"], "icon": p["icon"]})
    if not all_personas:
        return {"name": "Unknown", "icon": "?"}
    idx = (exchange_count - 1) % len(all_personas)
    return all_personas[idx]


# ============================================================
# Paper Scanning & Summary Section Parsing (v9.1.0)
# ============================================================
MAX_SUMMARY_CHARS = 4000

# Summary section names that can be referenced
SUMMARY_SECTIONS = [
    "Abstract",
    "Introduction & Motivation",
    "Methodology",
    "Experiments & Results",
    "Discussion & Conclusion",
    "Key Contributions",
    "Potential Relevance",
]


def parse_summary_sections(summary_path: Path) -> Dict[str, str]:
    """Parse a summary .md file into a dict of {section_name: content}.

    Handles both ## and ### level headers. Strips YAML frontmatter.

    Returns:
        Dict mapping section names (e.g. "Methodology") to their text content.
    """
    try:
        raw = summary_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"Cannot read summary {summary_path}: {e}")
        return {}

    # Strip YAML frontmatter
    if raw.startswith("---"):
        end_fm = raw.find("---", 3)
        if end_fm != -1:
            raw = raw[end_fm + 3:].strip()

    sections: Dict[str, str] = {}
    current_section = None
    current_lines: List[str] = []

    for line in raw.split("\n"):
        # Match ### Section or ## Section headers
        header_match = re.match(r'^#{2,3}\s+(.+)$', line)
        if header_match:
            # Save previous section
            if current_section is not None:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = header_match.group(1).strip()
            current_lines = []
        else:
            if current_section is not None:
                current_lines.append(line)

    # Save last section
    if current_section is not None:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def extract_sections(summary_path: Path, section_names: List[str]) -> str:
    """Extract specific sections from a summary file and return as formatted text.

    Args:
        summary_path: Path to the summary .md file.
        section_names: List of section names to extract (e.g. ["Methodology", "Experiments & Results"]).

    Returns:
        Formatted string with the requested sections, or empty string if none found.
    """
    all_sections = parse_summary_sections(summary_path)
    if not all_sections:
        return ""

    parts = []
    for name in section_names:
        # Try exact match first, then case-insensitive
        content = all_sections.get(name)
        if content is None:
            name_lower = name.lower()
            for key, val in all_sections.items():
                if key.lower() == name_lower:
                    content = val
                    break
        if content:
            parts.append(f"### {name}\n{content}")

    return "\n\n".join(parts)


def build_paper_meta_for_selection(research_folder: Path, config: Dict[str, Any]) -> Tuple[str, Dict[str, Path]]:
    """Build compact paper metadata for LLM 1's selection prompt.

    For each paper, includes: Key Contributions + Potential Relevance + section list.
    This gives LLM 1 enough context to decide which paper+section each persona should reference.

    Args:
        research_folder: Path to the research folder.
        config: Phase 2A config dict.

    Returns:
        Tuple of (formatted_text, paper_id_to_summary_path_mapping).
    """
    papers_config = config.get("papers", {})
    if not papers_config.get("enabled", False):
        return "", {}

    summaries_dir = research_folder / "paper_summaries"
    if not summaries_dir.exists():
        return "", {}

    summary_files = sorted(summaries_dir.glob("*_summary.md"))
    if not summary_files:
        return "", {}

    lines = ["## Available Papers for Reference", ""]
    paper_map: Dict[str, Path] = {}  # paper_id -> summary_path

    for idx, sf in enumerate(summary_files):
        paper_id = f"P{idx + 1}"
        stem = sf.stem.replace("_summary", "")
        paper_map[paper_id] = sf

        sections = parse_summary_sections(sf)

        # Extract title from first line of content
        title = stem.replace("_", " ").title()
        try:
            raw = sf.read_text(encoding="utf-8")
            for line in raw.split("\n"):
                if line.startswith("# ") and not line.startswith("## "):
                    title = line[2:].strip()
                    break
        except Exception:
            pass

        # Build compact meta: Key Contributions + Potential Relevance + section list
        contributions = sections.get("Key Contributions", "N/A")
        relevance = sections.get("Potential Relevance", "N/A")

        # List available section names
        available = [s for s in SUMMARY_SECTIONS if s in sections or
                     any(k.lower() == s.lower() for k in sections)]

        lines.append(f"[{paper_id}] {stem} — \"{title}\"")
        lines.append(f"  Key Contributions: {contributions}")
        lines.append(f"  Potential Relevance: {relevance}")
        lines.append(f"  Available Sections: {', '.join(available)}")
        lines.append("")

    return "\n".join(lines), paper_map


def find_papers(research_folder: Path, config: Dict[str, Any]) -> List[Dict[str, str]]:
    """Scan papers folder and load summaries for LLM context."""
    papers_config = config.get("papers", {})
    if not papers_config.get("enabled", False):
        return []

    folder_pattern = papers_config.get("folder_pattern", "papers/*.md")
    pattern_path = PurePosixPath(folder_pattern)
    papers_dir = research_folder / str(pattern_path.parent)
    file_glob = pattern_path.name

    if not papers_dir.exists():
        logger.info(f"Papers directory not found: {papers_dir}")
        return []

    summaries_dir = research_folder / "paper_summaries"

    papers = []
    for paper_file in papers_dir.glob(file_glob):
        try:
            content = paper_file.read_text(encoding="utf-8")
            title = paper_file.stem.replace("_", " ").title()
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            sections = []
            for line in content.split("\n"):
                if line.startswith("## "):
                    sections.append(line[3:].strip())

            summary = ""
            summary_file = summaries_dir / f"{paper_file.stem}_summary.md"
            if summary_file.exists():
                try:
                    raw_summary = summary_file.read_text(encoding="utf-8")
                    if raw_summary.startswith("---"):
                        end_fm = raw_summary.find("---", 3)
                        if end_fm != -1:
                            raw_summary = raw_summary[end_fm + 3 :].strip()
                    if len(raw_summary) > MAX_SUMMARY_CHARS:
                        raw_summary = raw_summary[:MAX_SUMMARY_CHARS] + "\n...(truncated)"
                    summary = raw_summary
                except Exception as e:
                    logger.warning(f"Error reading summary {summary_file}: {e}")

            papers.append({
                "filename": paper_file.name,
                "title": title,
                "sections": sections[:10],
                "summary": summary,
            })
        except Exception as e:
            logger.warning(f"Error reading paper {paper_file}: {e}")

    summary_count = sum(1 for p in papers if p.get("summary"))
    logger.info(f"Found {len(papers)} papers ({summary_count} with summaries)")
    return papers


def build_papers_list(papers: List[Dict[str, str]], config: Dict[str, Any] = None) -> str:
    """Build markdown paper reference section for LLM 2 prompt (full summaries)."""
    if not papers:
        return ""

    lines = ["## Available Papers (with Summaries)", ""]
    for paper in papers:
        lines.append(f"### {paper['title']}")
        lines.append(f"**File:** `{paper['filename']}`")
        if paper.get("summary"):
            lines.append("")
            lines.append(paper["summary"])
        else:
            sections_str = ", ".join(paper["sections"][:5]) if paper["sections"] else "No sections"
            lines.append(f"**Sections:** {sections_str}")
            lines.append("*(No summary available)*")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# Discussion Analysis
# ============================================================
def count_exchanges(content: str) -> int:
    """Count number of exchanges in discussion."""
    return content.count("### Exchange")


def get_recent_speakers(content: str, icons: List[str], last_n: int = 3) -> list:
    """Get the last N speaker icons to avoid repetition."""
    speakers = []
    lines = content.split("\n")
    for line in reversed(lines):
        for icon in icons:
            if line.startswith(icon):
                if icon not in speakers:
                    speakers.append(icon)
                break
        if len(speakers) >= last_n:
            break
    return speakers


def get_recent_exchanges(content: str, last_n: int = 3) -> str:
    """Extract the last N exchanges from discussion content."""
    parts = content.split("### Exchange")
    if len(parts) <= 1:
        return content
    exchange_parts = parts[1:]
    recent = exchange_parts[-last_n:] if len(exchange_parts) > last_n else exchange_parts
    result_parts = []
    for part in recent:
        result_parts.append("### Exchange" + part)
    return "\n".join(result_parts)


# ============================================================
# OpenRouter LLM Call (with retry)
# ============================================================
def call_openrouter(prompt: str, config: Dict[str, Any], label: str = "LLM") -> Optional[str]:
    """Call OpenRouter LLM with 15-second retry (3 attempts)."""
    openrouter_config = config.get("openrouter", {})
    api_key_env = openrouter_config.get("api_key_env", "OPENROUTER_API_KEY")
    api_key = os.environ.get(api_key_env)

    if not api_key:
        logger.error(f"[{label}] API key not found: {api_key_env}")
        return None

    model = openrouter_config.get("model", "openai/gpt-5.2-chat")
    timeout = openrouter_config.get("timeout_seconds", 60)
    max_tokens = openrouter_config.get("max_tokens", 1000)

    debug_config = config.get("debug", {})
    log_llm = debug_config.get("log_llm_interactions", False)

    for attempt in range(1, 4):
        try:
            logger.info(f"[{label}] Calling LLM ({model}), attempt {attempt}/3...")

            if log_llm:
                logger.debug(f"[{label}] PROMPT:\n{prompt}")

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "X-Title": f"YouRA Phase 2A Orchestrator ({label})",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
                timeout=timeout,
            )

            if response.status_code != 200:
                logger.error(f"[{label}] HTTP {response.status_code}: {response.text[:200]}")
                if attempt < 3:
                    logger.info(f"[{label}] Retrying in 15s...")
                    time.sleep(15)
                    continue
                return None

            result = response.json()
            llm_response = result["choices"][0]["message"]["content"]
            logger.info(f"[{label}] Response received ({len(llm_response)} chars)")

            if log_llm:
                logger.debug(f"[{label}] RESPONSE:\n{llm_response}")

            return llm_response

        except requests.exceptions.Timeout:
            logger.error(f"[{label}] Request timed out (attempt {attempt}/3)")
            if attempt < 3:
                time.sleep(15)
                continue
            return None
        except Exception as e:
            logger.error(f"[{label}] Call failed: {e} (attempt {attempt}/3)")
            if attempt < 3:
                time.sleep(15)
                continue
            return None

    return None


# ============================================================
# LLM 1: Selection + Convergence Check
# ============================================================
def build_selection_prompt(
    discussion_content: str,
    config: Dict[str, Any],
    personas_data: Dict[str, Any],
    paper_meta: str = "",
) -> str:
    """Build prompt for LLM 1: persona selection + convergence check + paper reference assignment."""
    icons = get_all_icons(personas_data)
    exchange_count = count_exchanges(discussion_content)
    recent_speakers = get_recent_speakers(discussion_content, icons)

    discussion_config = config.get("discussion", {})
    convergence = personas_data.get("convergence", {})
    min_exchanges = discussion_config.get("min_exchanges", convergence.get("min_exchanges", 15))
    max_exchanges = discussion_config.get("max_exchanges", convergence.get("max_exchanges", 50))
    personas_per_exchange = discussion_config.get("personas_per_exchange", 2)

    persona_roster = build_persona_roster(personas_data)
    convergence_checklist = build_convergence_checklist(personas_data)

    recent_discussion = get_recent_exchanges(discussion_content, last_n=4)

    # Paper reference section (only if papers are available)
    paper_ref_section = ""
    paper_ref_json_hint = ""
    if paper_meta:
        paper_ref_section = f"""
{paper_meta}

### Step 3: Assign Paper References (optional but encouraged)
For each selected persona, you MAY assign a paper and specific sections to reference.
This helps the persona ground their arguments in actual research evidence.
- Look at the paper contributions and relevance above
- Choose sections that are most useful for the persona's role
  (e.g., Falsifiability Expert → Methodology/Experiments, Novelty Explorer → Key Contributions)
- You can assign different papers/sections to each persona, or skip if no paper is relevant
"""
        paper_ref_json_hint = ', "paper_references": {{"llm_persona": {{"paper": "P1", "sections": ["Methodology", "Experiments & Results"]}}, "claude_persona": {{"paper": "P2", "sections": ["Methodology"]}}}}'

    prompt = f"""You are the Orchestrator for a research hypothesis discussion.

## Recent Discussion (last 4 exchanges)
```
{recent_discussion}
```

## Statistics
- Exchange count: {exchange_count}
- Minimum for convergence: {min_exchanges}
- Maximum allowed: {max_exchanges}
- Recent speakers (avoid repeating): {recent_speakers}

## Persona Roster (name and role only)
{persona_roster}

## Your Task

### Step 1: Check Convergence (only if exchange_count >= {min_exchanges})
{convergence_checklist}

If ALL criteria met → respond with EXACTLY:
```
CONVERGE
Key achievements:
- [Point 1]
- [Point 2]
```

### Step 2: If NOT converged, select TWO different personas
- Select EXACTLY 2 personas: one for the external LLM to write, one for Claude to write
- The two personas must be DIFFERENT from each other
- Avoid recent speakers if possible: {recent_speakers}
- Choose based on what aspects of the hypothesis are weakest
{paper_ref_section}

Respond with EXACTLY this JSON format (no other text):
```json
{{"llm_persona": "Prof. Vera", "claude_persona": "Dr. Nova", "reason": "need testability check and creative alternatives"{paper_ref_json_hint}}}
```

IMPORTANT: Output ONLY "CONVERGE..." or the JSON block. Nothing else.
"""
    return prompt


def parse_selection_response(
    response: str, personas_data: Dict[str, Any], exchange_count: int
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]], str, Optional[Dict[str, Any]]]:
    """
    Parse LLM 1 response.

    Returns:
        (is_converged, llm_persona, claude_persona, reason, paper_references)

    paper_references format (may be None):
        {"llm_persona": {"paper": "P1", "sections": ["Methodology"]},
         "claude_persona": {"paper": "P2", "sections": ["Experiments & Results"]}}
    """
    stripped = response.strip()

    if stripped.startswith("CONVERGE"):
        return True, None, None, stripped, None

    # Match potentially nested JSON (paper_references contains nested objects)
    # Find the outermost { ... } block
    brace_depth = 0
    json_start = None
    json_end = None
    for i, ch in enumerate(stripped):
        if ch == '{':
            if brace_depth == 0:
                json_start = i
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
            if brace_depth == 0 and json_start is not None:
                json_end = i + 1
                break

    if json_start is None or json_end is None:
        logger.warning(f"LLM-1 response not parseable: {stripped[:200]}")
        return False, None, None, "[ERROR] Could not parse persona selection", None

    try:
        selection = json.loads(stripped[json_start:json_end])
    except json.JSONDecodeError as e:
        logger.warning(f"LLM-1 JSON parse error: {e}")
        return False, None, None, f"[ERROR] JSON parse error: {e}", None

    reason = selection.get("reason", "")
    paper_references = selection.get("paper_references", None)

    if paper_references:
        logger.info(f"LLM-1 assigned paper references: {json.dumps(paper_references)}")

    # Parse dual-persona format
    llm_name = selection.get("llm_persona", "")
    claude_name = selection.get("claude_persona", "")

    # Fallback: "personas" list format
    if not llm_name and not claude_name:
        fallback_names = selection.get("personas", [])
        if len(fallback_names) >= 2:
            llm_name, claude_name = fallback_names[0], fallback_names[1]
        elif len(fallback_names) == 1:
            llm_name = fallback_names[0]

    # Validate llm_persona
    llm_persona = find_persona_by_name(personas_data, llm_name) if llm_name else None
    if llm_persona:
        logger.info(f"LLM-1 selected for LLM: {llm_persona['icon']} {llm_persona['name']}")
    else:
        logger.warning(f"LLM persona invalid: '{llm_name}', using round-robin")
        fallback = get_next_round_robin_persona(exchange_count + 1, personas_data)
        llm_persona = find_persona_by_name(personas_data, fallback["name"])

    # Validate claude_persona
    claude_persona = find_persona_by_name(personas_data, claude_name) if claude_name else None
    if claude_persona:
        logger.info(f"LLM-1 selected for Claude: {claude_persona['icon']} {claude_persona['name']}")
    else:
        # Pick a different persona from llm_persona via round-robin
        logger.warning(f"Claude persona invalid: '{claude_name}', using round-robin")
        fallback = get_next_round_robin_persona(exchange_count + 2, personas_data)
        claude_persona = find_persona_by_name(personas_data, fallback["name"])
        # Ensure different from llm_persona
        if claude_persona and llm_persona and claude_persona["name"] == llm_persona["name"]:
            fallback = get_next_round_robin_persona(exchange_count + 3, personas_data)
            claude_persona = find_persona_by_name(personas_data, fallback["name"])

    return False, llm_persona, claude_persona, reason, paper_references


# ============================================================
# LLM 2: Full Exchange Generation
# ============================================================
def build_exchange_prompt(
    discussion_content: str,
    llm_persona: Dict[str, Any],
    exchange_number: int,
    config: Dict[str, Any],
    papers: List[Dict[str, str]] = None,
    selection_reason: str = "",
    paper_reference: Optional[Dict[str, Any]] = None,
    paper_map: Optional[Dict[str, Path]] = None,
) -> str:
    """Build prompt for LLM 2: generate a full Exchange response as the persona.

    Args:
        paper_reference: LLM 1's assigned paper reference for this persona,
            e.g. {"paper": "P1", "sections": ["Methodology", "Experiments & Results"]}
        paper_map: Mapping from paper_id (e.g. "P1") to summary file path.
    """
    recent_discussion = get_recent_exchanges(discussion_content, last_n=4)

    persona_detail = build_persona_detail(llm_persona)

    # Build targeted paper context from assigned reference
    paper_context = ""
    if paper_reference and paper_map:
        paper_id = paper_reference.get("paper", "")
        section_names = paper_reference.get("sections", [])
        summary_path = paper_map.get(paper_id)

        if summary_path and summary_path.exists() and section_names:
            extracted = extract_sections(summary_path, section_names)
            if extracted:
                stem = summary_path.stem.replace("_summary", "")
                paper_context = f"""
## Assigned Paper Reference — {stem}
The orchestrator has assigned the following paper sections for you to reference in your response.
Ground your arguments in this evidence where relevant.

{extracted}
"""
                logger.info(
                    f"Injected paper sections for LLM persona: {paper_id} -> {section_names}"
                )

    # Fallback: include full paper list if no targeted reference
    if not paper_context and papers:
        paper_context = "\n" + build_papers_list(papers, config)

    prompt = f"""You are participating in a research hypothesis discussion as a specific persona.

## Your Persona — Full Definition
{persona_detail}

## Selection Context
Reason you were selected: {selection_reason}

## Recent Discussion (last 4 exchanges)
{recent_discussion}
{paper_context}

## Your Task

Write a substantive research discussion response **in character** as {llm_persona['icon']} **{llm_persona['name']}** ({llm_persona['title']}).

### Requirements:
- Write 3-6 paragraphs of genuine research discussion
- Stay fully in character (use the persona's communication style, principles, and focus areas)
- Reference specific points from the recent discussion (agree, disagree, build upon)
- If paper sections are provided above, cite specific findings/methods from them using [Author et al., Year]
- Propose concrete mechanisms, predictions, or experiments where relevant
- End with 3 Key Points summarizing your contribution

### Output Format (output ONLY this, no preamble):

{llm_persona['icon']} **{llm_persona['name']}** ({llm_persona['title']}):

[Your 3-6 paragraph response in character]

**Key Points:**
- [Point 1]
- [Point 2]
- [Point 3]
"""
    return prompt


# ============================================================
# Main Orchestration Logic
# ============================================================
def orchestrate(
    discussion_content: str,
    config: Dict[str, Any],
    personas_data: Dict[str, Any],
    research_folder: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Main orchestration: select persona + check convergence + generate instructions.

    Returns dict suitable for JSON stdout output.
    """
    exchange_count = count_exchanges(discussion_content)
    convergence = personas_data.get("convergence", {})
    discussion_config = config.get("discussion", {})
    max_exchanges = discussion_config.get("max_exchanges", convergence.get("max_exchanges", 50))
    min_exchanges = discussion_config.get("min_exchanges", convergence.get("min_exchanges", 15))

    # Force convergence at max
    if exchange_count >= max_exchanges:
        logger.info(f"Max exchanges ({max_exchanges}) reached, forcing convergence")
        return {
            "converged": True,
            "exchange_number": exchange_count,
            "summary": "Maximum exchange limit reached. Proceeding to Final Assessments.",
        }

    # Scan papers if research folder provided
    papers = []
    paper_meta = ""
    paper_map: Dict[str, Path] = {}
    if research_folder:
        papers = find_papers(research_folder, config)
        paper_meta, paper_map = build_paper_meta_for_selection(research_folder, config)

    openrouter_config = config.get("openrouter", {})
    if not openrouter_config.get("enabled", True):
        # LLM disabled → round-robin fallback
        return _round_robin_fallback(exchange_count, personas_data)

    api_key_env = openrouter_config.get("api_key_env", "OPENROUTER_API_KEY")
    if not os.environ.get(api_key_env):
        logger.error(f"{api_key_env} not set, falling back to round-robin")
        return _round_robin_fallback(exchange_count, personas_data)

    # ── Phase 1: Selection (2 personas: LLM + Claude) ──
    turn_mode = discussion_config.get("turn_mode", "intelligent")
    paper_references = None

    if turn_mode == "round-robin":
        # Round-robin: code-determined, pick 2 sequential personas
        rr1 = get_next_round_robin_persona(exchange_count + 1, personas_data)
        rr2 = get_next_round_robin_persona(exchange_count + 2, personas_data)
        llm_persona = find_persona_by_name(personas_data, rr1["name"])
        claude_persona = find_persona_by_name(personas_data, rr2["name"])
        selection_reason = f"round-robin rotation (exchanges {exchange_count + 1}-{exchange_count + 2})"

        # Still check convergence if past min
        if exchange_count >= min_exchanges:
            selection_prompt = build_selection_prompt(discussion_content, config, personas_data, paper_meta)
            llm1_response = call_openrouter(selection_prompt, config, "LLM-1-Convergence")
            if llm1_response and llm1_response.strip().startswith("CONVERGE"):
                return {
                    "converged": True,
                    "exchange_number": exchange_count,
                    "summary": llm1_response,
                }
    else:
        # intelligent / free mode — LLM 1 selects 2 personas + paper references
        selection_prompt = build_selection_prompt(discussion_content, config, personas_data, paper_meta)
        llm1_response = call_openrouter(selection_prompt, config, "LLM-1-Selection")

        if llm1_response is None:
            logger.warning("LLM-1 failed, falling back to round-robin")
            return _round_robin_fallback(exchange_count, personas_data)

        is_converged, llm_persona, claude_persona, selection_reason, paper_references = (
            parse_selection_response(llm1_response, personas_data, exchange_count)
        )

        if is_converged:
            return {
                "converged": True,
                "exchange_number": exchange_count,
                "summary": selection_reason,
            }

        if not llm_persona:
            return _round_robin_fallback(exchange_count, personas_data)

    # ── Phase 2: LLM writes full Exchange ──
    next_exchange = exchange_count + 1

    # Extract LLM persona's paper reference (if assigned by LLM 1)
    llm_paper_ref = None
    if paper_references and isinstance(paper_references, dict):
        llm_paper_ref = paper_references.get("llm_persona")

    exchange_prompt = build_exchange_prompt(
        discussion_content, llm_persona, next_exchange, config, papers, selection_reason,
        paper_reference=llm_paper_ref, paper_map=paper_map,
    )

    # Use higher max_tokens for full exchange generation
    original_max_tokens = config.get("openrouter", {}).get("max_tokens", 1000)
    config.setdefault("openrouter", {})["max_tokens"] = max(original_max_tokens, 2000)

    llm2_response = call_openrouter(exchange_prompt, config, "LLM-2-Exchange")

    # Restore original max_tokens
    config["openrouter"]["max_tokens"] = original_max_tokens

    # Extract Claude persona's paper reference for the output JSON
    claude_paper_ref = None
    if paper_references and isinstance(paper_references, dict):
        claude_paper_ref = paper_references.get("claude_persona")

    if llm2_response is None:
        # Fallback: Claude writes both
        result = {
            "converged": False,
            "exchange_number": next_exchange,
            "llm_exchange": None,
            "llm_persona": {"name": llm_persona["name"], "icon": llm_persona["icon"]} if llm_persona else None,
            "claude_persona": {"name": claude_persona["name"], "icon": claude_persona["icon"]} if claude_persona else None,
            "fallback": True,
        }
        if claude_paper_ref:
            result["claude_paper_reference"] = claude_paper_ref
        return result

    result = {
        "converged": False,
        "exchange_number": next_exchange,
        "llm_exchange": llm2_response.strip(),
        "llm_persona": {"name": llm_persona["name"], "icon": llm_persona["icon"]},
        "claude_persona": {"name": claude_persona["name"], "icon": claude_persona["icon"]},
    }
    if claude_paper_ref:
        result["claude_paper_reference"] = claude_paper_ref
    return result


def _round_robin_fallback(exchange_count: int, personas_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate round-robin fallback (no LLM needed). Claude writes both exchanges."""
    rr1 = get_next_round_robin_persona(exchange_count + 1, personas_data)
    rr2 = get_next_round_robin_persona(exchange_count + 2, personas_data)
    p1 = find_persona_by_name(personas_data, rr1["name"])
    p2 = find_persona_by_name(personas_data, rr2["name"])
    return {
        "converged": False,
        "exchange_number": exchange_count + 1,
        "llm_exchange": None,
        "llm_persona": {"name": p1["name"], "icon": p1["icon"]} if p1 else None,
        "claude_persona": {"name": p2["name"], "icon": p2["icon"]} if p2 else None,
        "fallback": True,
    }


# ============================================================
# CLI Entry Point
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Phase 2A Discussion Orchestrator (Standalone)"
    )
    parser.add_argument(
        "--discussion-log",
        required=True,
        help="Path to discussion_log.md",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to phase2a_config.yaml (default: scripts/phase2a_config.yaml)",
    )
    parser.add_argument(
        "--personas",
        default=None,
        help="Path to personas.yaml",
    )
    parser.add_argument(
        "--research-folder",
        default=None,
        help="Path to research folder (for paper scanning)",
    )

    args = parser.parse_args()

    # Resolve paths
    discussion_log_path = Path(args.discussion_log)
    if not discussion_log_path.exists():
        print(json.dumps({"error": f"discussion_log.md not found: {discussion_log_path}"}))
        sys.exit(1)

    # Config: default to same directory as this script
    if args.config:
        config_path = Path(args.config)
    else:
        config_path = Path(__file__).parent / "phase2a_config.yaml"

    # Personas: search common locations
    if args.personas:
        personas_path = Path(args.personas)
    else:
        personas_path = Path(__file__).parent.parent / "personas.yaml"

    research_folder = Path(args.research_folder) if args.research_folder else None

    # Load
    config = load_config(config_path)
    personas_data = load_personas(personas_path)

    # Read discussion log
    try:
        discussion_content = discussion_log_path.read_text(encoding="utf-8")
    except Exception as e:
        print(json.dumps({"error": f"Cannot read discussion log: {e}"}))
        sys.exit(1)

    if not discussion_content.strip():
        print(json.dumps({"error": "Discussion log is empty"}))
        sys.exit(1)

    # Orchestrate
    result = orchestrate(discussion_content, config, personas_data, research_folder)

    # Output JSON to stdout
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
