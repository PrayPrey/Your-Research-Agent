"""Run the LLM-as-Judge pairwise paper comparison from explicit file paths.

Examples:
    python analysis/LLM_as_Judge_main/run_llm_as_judge.py \
        --paper-a path/to/youra.md \
        --paper-b path/to/baseline.pdf \
        --task path/to/task.md \
        --label-a YouRA \
        --label-b "AI Scientist v2" \
        --output analysis/LLM_as_Judge_main/custom_results.json

If arguments are omitted, the script prompts for the paths interactively.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


SUPPORTED_JUDGE_MODELS = (
    "google/gemini-3.1-pro-preview",
    "openai/gpt-5.4",
    "x-ai/grok-4.3",
    "anthropic/claude-opus-4.6",
)
DEFAULT_JUDGE_MODEL = "google/gemini-3.1-pro-preview"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

EVALUATION_RUBRIC = """
## Evaluation Rubric

1. Clarity (1-10)
    - Is the paper well-written and easy to understand?
    - Are the ideas and contributions clearly articulated?
    - Is the structure of the paper logical and coherent?

    9-10 - The paper is exceptionally well-written, with clear and concise language. The ideas are presented in a logical and coherent manner, making it easy to follow the author's arguments.
    7-8 - The paper is well-written, but there are some areas that could be improved for clarity. The ideas are mostly clear, but there may be some minor issues with the structure or language.
    5-6 - The paper is somewhat difficult to read, with several areas that are unclear or poorly articulated. The structure may be confusing, making it hard to follow the author's arguments.
    3-4 - The paper is poorly written, with many unclear or confusing sections. The ideas are not well-articulated, and the structure is disorganized.
    1-2 - The paper is extremely difficult to read, with numerous unclear or confusing sections. The ideas are poorly articulated, and the structure is completely disorganized.

2. Novelty (1-10)
    - Does the paper present new and original ideas and findings?
    - Are the experimental results and contributions original and novel?
    - Is the work a significant advance over existing research?

    9-10 - The paper presents groundbreaking ideas and findings that are highly original and significant. The contributions are a major advance over existing research and are likely to have a lasting impact on the field.
    7-8 - The paper presents some new and original ideas, and the contributions are significant. The work is a notable advance over existing research, but it may not be as groundbreaking as top-tier papers.
    5-6 - The paper presents some new ideas and findings, but they are not particularly original or significant. The contributions are somewhat incremental and do not represent a major advance over existing research.
    3-4 - The paper presents few new ideas or findings, and those that are presented are not original or significant. The contributions are minimal and do not advance the field.
    1-2 - The paper presents no new ideas, and the contributions are completely unoriginal. The work does not advance the field in any meaningful way.

3. Soundness (1-10)
    - Are the methods and techniques used in the paper sound and appropriate?
    - Are the results and conclusions supported by the data?
    - Are there any major flaws or weaknesses in the experimental design, results or analysis?
    - Are the experimental results reliable and consistent to the code of the paper? Are the experimental results real or fake?
    - Are the visualization and analysis figures based on real experimental results or based on fake data?

    9-10 - The methods and techniques used in the paper are sound and appropriate. The results are well-supported by the data, and there are no major flaws or weaknesses in the experimental design, results or analysis. The experimental results are fully reliable and consistent with the code of the paper.
    7-8 - The methods and techniques used in the paper are mostly sound, but there may be some minor issues. The results are generally well-supported by the data, but there may be some areas that could be improved. The experimental design, results or analysis may have some minor flaws. The experimental results are mostly reliable.
    5-6 - The methods and techniques used in the paper are somewhat questionable, with several areas that could be improved. The results are not well-supported by the data, and there may be some significant flaws in the experimental design, results or analysis. Some experimental results are not reliable.
    3-4 - The methods and techniques used in the paper are flawed or inappropriate. The results are not well-supported by the data, and there are major flaws in the experimental design, results or analysis. Most of experimental results are not reliable.
    1-2 - The methods and techniques used in the paper are completely unsound. The results are not supported by the data, and there are numerous major flaws in the experimental design, results or analysis. The conclusions drawn from the paper are completely invalid. All experimental results are not reliable.

4. Significance (1-10)
    - Does the paper address an important problem or question?
    - Are the contributions significant to the field?
    - Are the experimental results reproducible and reliable? Do they have a significant impact?
    - Will the work have a lasting impact on the field?

    9-10 - The paper addresses a highly important problem or question, and the results and contributions are significant to the field. The work is likely to have a lasting impact on the field.
    7-8 - The paper addresses an important problem or question, and the results and contributions are significant. The work may have a lasting impact on the field, but it may not be as groundbreaking as top-tier papers.
    5-6 - The paper addresses a somewhat important problem or question, but the results and contributions are not particularly significant. The work may have some impact on the field, but it is unlikely to be lasting.
    3-4 - The paper addresses a minor problem or question, and the results and contributions are minimal. The work is unlikely to have any significant impact on the field.
    1-2 - The paper addresses an unimportant problem or question, and the results and contributions are completely insignificant. The work will have no impact on the field.

5. Overall Assessment (1-10)
    - Based on the above criteria, how would you rate the overall quality of the paper? Note that any single weakness can be critical to lower the overall assessment.
    - Is the paper suitable for publication in a top-tier conference or journal?
    - Would you recommend this paper to your colleagues?

    10 - The paper is of exceptional quality and is highly suitable for publication in a top-tier conference or journal. I would strongly recommend this paper.
    8-9 - The paper is of high quality and is suitable for publication in a top-tier conference or journal. I would recommend this paper.
    6-7 - The paper is of good quality and is suitable for publication in a reputable conference or journal. I would recommend this paper with some reservations.
    4-5 - The paper is of acceptable quality but may not be suitable for publication in a top-tier conference or journal. I would recommend this paper with significant reservations.
    2-3 - The paper is of poor quality and is not suitable for publication in a top-tier conference or journal. I would not recommend this paper.
    1 - The paper is of extremely poor quality and is not suitable for publication in any conference or journal. I would strongly advise against recommending this paper.

6. Confidence Score (1-5)
    - How confident are you in your overall assessment of the paper?

    5 - Extremely confident in the overall assessment.
    4 - Very confident in the overall assessment.
    3 - Moderately confident in the overall assessment.
    2 - Slightly confident in the overall assessment.
    1 - Not confident in the overall assessment.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two research papers with the existing LLM-as-Judge rubric.",
    )
    parser.add_argument("--paper-a", help="Path to Paper A (.md, .txt, .pdf, or .json).")
    parser.add_argument("--paper-b", help="Path to Paper B (.md, .txt, .pdf, or .json).")
    parser.add_argument("--task", help="Optional task-description file path.")
    parser.add_argument("--task-text", help="Optional task description text.")
    parser.add_argument("--label-a", default="Paper A", help="Display label for Paper A.")
    parser.add_argument("--label-b", default="Paper B", help="Display label for Paper B.")
    parser.add_argument(
        "--judge-model",
        default=os.getenv("LLM_JUDGE_MODEL", DEFAULT_JUDGE_MODEL),
        choices=SUPPORTED_JUDGE_MODELS,
        help=(
            "OpenRouter judge model ID. Only the four supported models are accepted: "
            + ", ".join(SUPPORTED_JUDGE_MODELS)
            + f". Default: {DEFAULT_JUDGE_MODEL}."
        ),
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL),
        help="OpenAI-compatible API base URL.",
    )
    parser.add_argument(
        "--api-key-env",
        default="OPENROUTER_API_KEY",
        help="Environment variable that stores the API key.",
    )
    parser.add_argument(
        "--output",
        default="analysis/LLM_as_Judge_main/custom_llm_judge_results.json",
        help="Output JSON path. CSV is written next to it.",
    )
    parser.add_argument(
        "--single-round",
        action="store_true",
        help="Run only Paper A vs Paper B. Default runs A/B and B/A to detect position bias.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and write the prompts without calling the judge API.",
    )
    args = parser.parse_args()
    if args.judge_model not in SUPPORTED_JUDGE_MODELS:
        raise SystemExit(
            f"Unsupported judge model: {args.judge_model!r}. "
            f"Supported models: {', '.join(SUPPORTED_JUDGE_MODELS)}."
        )
    return args


def prompt_if_missing(value: str | None, label: str, required: bool = True) -> str | None:
    if value:
        return value
    suffix = "" if required else " (optional, press Enter to skip)"
    answer = input(f"{label}{suffix}: ").strip()
    if required and not answer:
        raise SystemExit(f"{label} is required.")
    return answer or None


def load_dotenv_if_available() -> None:
    try:
        from dotenv import find_dotenv, load_dotenv
    except ImportError:
        return
    load_dotenv(find_dotenv())


def read_document(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            import pymupdf
        except ImportError as exc:
            raise RuntimeError("Reading PDFs requires pymupdf. Install project dependencies first.") from exc

        doc = pymupdf.open(path)
        try:
            return "\n".join(page.get_text() for page in doc)
        finally:
            doc.close()

    if suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, ensure_ascii=False, indent=2)

    with path.open("r", encoding="utf-8") as f:
        return f.read()


def build_judge_prompt(task_input: str, paper_a: str, paper_b: str, label_a: str, label_b: str) -> str:
    return f"""You are an expert machine learning researcher acting as a Senior Area Chair at a top-tier AI conference.
You will be given a task description and TWO research papers (Paper A and Paper B) generated based on that task.
Your goal is to review and compare both papers using the evaluation rubric below.

Please provide scores from 1 to 10 for each aspect for BOTH papers, and determine a winner.
Do not hesitate to assign lower scores if the paper does not fully meet the criteria. Avoid giving high scores by default.
Note that any single weakness can be critical to lower the overall assessment.

IMPORTANT: You MUST choose a winner. There is NO tie option. Even if the papers are close in quality, you must decide which one is better overall.

**[Task Description]**
{task_input}

**[Paper A: {label_a}]**
{paper_a}

**[Paper B: {label_b}]**
{paper_b}

{EVALUATION_RUBRIC}

**[Review Guidelines]**
- Review each paper independently first, then compare them.
- Be objective and base your review solely on the content of the papers.
- Penalize papers that contain hallucinated results, fake experimental data, or unsupported claims.
- Favor papers that define a specific, well-scoped problem and provide sound methodology.
- You MUST pick a winner. Do NOT output "tie".

**[Output Format]**
Provide your response in JSON format ONLY:

{{
  "analysis": "<Detailed comparison of Paper A and Paper B across all criteria>",
  "scores_paper_a": {{
    "clarity": <int 1-10>,
    "novelty": <int 1-10>,
    "soundness": <int 1-10>,
    "significance": <int 1-10>,
    "overall": <int 1-10>,
    "confidence": <int 1-5>,
    "total": <sum of clarity+novelty+soundness+significance+overall>
  }},
  "scores_paper_b": {{
    "clarity": <int 1-10>,
    "novelty": <int 1-10>,
    "soundness": <int 1-10>,
    "significance": <int 1-10>,
    "overall": <int 1-10>,
    "confidence": <int 1-5>,
    "total": <sum of clarity+novelty+soundness+significance+overall>
  }},
  "winner": "paper_a" | "paper_b"
}}

IMPORTANT: You MUST choose either "paper_a" or "paper_b" as the winner. Do NOT output "tie".
Please ensure that your output is a complete and valid JSON object. Do not output partial content.
Please provide detailed justifications in the analysis field, including specific examples from both papers.
"""


def make_client(api_key_env: str, base_url: str) -> Any:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The openai package is required. Install project dependencies first.") from exc

    api_key = os.getenv(api_key_env)
    if not api_key:
        raise RuntimeError(f"Missing API key. Set {api_key_env} in your environment or .env file.")
    return OpenAI(api_key=api_key, base_url=base_url)


def call_judge(client: Any, judge_model: str, prompt: str) -> str | None:
    try:
        completion = client.chat.completions.create(
            model=judge_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a fair and rigorous academic reviewer. Output JSON only. You must always pick a winner.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content
    except Exception as exc:
        print(f"  [API Error] {exc}")
        time.sleep(2)
        return None


def parse_result(response_text: str | None) -> dict[str, Any]:
    if not response_text:
        return {"winner": "error", "reasoning": "No response from judge"}
    try:
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        return {"winner": "error", "reasoning": "Parsing failed", "raw_response": response_text}

    if result.get("winner") == "tie":
        result["winner"] = "error"
        result["reasoning"] = "Judge returned tie despite forced-choice instruction"
    return result


def evaluate_pair(
    client: Any,
    judge_model: str,
    task_text: str,
    paper_a: str,
    paper_b: str,
    label_a: str,
    label_b: str,
    single_round: bool,
) -> dict[str, Any]:
    prompt_1 = build_judge_prompt(task_text, paper_a, paper_b, label_a, label_b)
    round1 = parse_result(call_judge(client, judge_model, prompt_1))

    if single_round:
        winner = round1.get("winner", "error")
        verdict = "Win" if winner == "paper_a" else "Lose" if winner == "paper_b" else "Error"
        return {"round1": round1, "round2": None, "verdict": verdict}

    prompt_2 = build_judge_prompt(task_text, paper_b, paper_a, label_b, label_a)
    round2 = parse_result(call_judge(client, judge_model, prompt_2))

    valid_winners = {"paper_a", "paper_b"}
    if round1.get("winner") not in valid_winners or round2.get("winner") not in valid_winners:
        return {"round1": round1, "round2": round2, "verdict": "Error"}

    a_won_round1 = round1.get("winner") == "paper_a"
    a_won_round2 = round2.get("winner") == "paper_b"
    if a_won_round1 and a_won_round2:
        verdict = "Win"
    elif not a_won_round1 and not a_won_round2:
        verdict = "Lose"
    else:
        verdict = "Tie"
    return {"round1": round1, "round2": round2, "verdict": verdict}


def write_csv(result: dict[str, Any], output_json: Path) -> Path:
    csv_path = output_json.with_suffix(".csv")
    detail = result["detail"]
    round1 = detail.get("round1") or {}
    round2 = detail.get("round2") or {}
    label_a = result["label_a"]
    label_b = result["label_b"]

    row = {
        "comparison": result["comparison"],
        "label_a": label_a,
        "label_b": label_b,
        "r1_winner": {"paper_a": label_a, "paper_b": label_b}.get(round1.get("winner"), round1.get("winner", "")),
        "r2_winner": {"paper_a": label_b, "paper_b": label_a}.get(round2.get("winner"), round2.get("winner", "")),
        "verdict": detail.get("verdict", ""),
    }

    for prefix, scores in (
        ("r1_a", round1.get("scores_paper_a", {})),
        ("r1_b", round1.get("scores_paper_b", {})),
        ("r2_b_as_a", round2.get("scores_paper_a", {})),
        ("r2_a_as_b", round2.get("scores_paper_b", {})),
    ):
        for key in ("clarity", "novelty", "soundness", "significance", "overall", "confidence", "total"):
            row[f"{prefix}_{key}"] = scores.get(key, "")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)
    return csv_path


def main() -> int:
    load_dotenv_if_available()
    args = parse_args()

    interactive_mode = not args.paper_a or not args.paper_b
    paper_a_path = Path(prompt_if_missing(args.paper_a, "Paper A path")).expanduser()
    paper_b_path = Path(prompt_if_missing(args.paper_b, "Paper B path")).expanduser()

    task_path_value = args.task
    if interactive_mode and not args.task_text and not task_path_value:
        task_path_value = prompt_if_missing(None, "Task description path", required=False)

    paper_a = read_document(paper_a_path)
    paper_b = read_document(paper_b_path)
    if args.task_text:
        task_text = args.task_text
        task_path = None
    elif task_path_value:
        task_path = Path(task_path_value).expanduser()
        task_text = read_document(task_path)
    else:
        task_path = None
        task_text = "No separate task description was provided. Evaluate the papers based on their stated problem, claims, methodology, and evidence."

    output_json = Path(args.output)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    prompt_1 = build_judge_prompt(task_text, paper_a, paper_b, args.label_a, args.label_b)
    prompt_2 = None
    if not args.single_round:
        prompt_2 = build_judge_prompt(task_text, paper_b, paper_a, args.label_b, args.label_a)

    if args.dry_run:
        result_detail = {
            "round1_prompt_chars": len(prompt_1),
            "round2_prompt_chars": len(prompt_2) if prompt_2 else 0,
            "verdict": "DryRun",
        }
    else:
        client = make_client(args.api_key_env, args.base_url)
        result_detail = evaluate_pair(
            client=client,
            judge_model=args.judge_model,
            task_text=task_text,
            paper_a=paper_a,
            paper_b=paper_b,
            label_a=args.label_a,
            label_b=args.label_b,
            single_round=args.single_round,
        )

    result = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "judge_model": args.judge_model,
        "comparison": f"{args.label_a} vs {args.label_b}",
        "label_a": args.label_a,
        "label_b": args.label_b,
        "paper_a_path": str(paper_a_path),
        "paper_b_path": str(paper_b_path),
        "task_path": str(task_path) if task_path else None,
        "task_text_provided": bool(args.task_text),
        "single_round": args.single_round,
        "dry_run": args.dry_run,
        "detail": result_detail,
    }

    if args.dry_run:
        result["prompts"] = {"round1": prompt_1, "round2": prompt_2}

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    csv_path = write_csv(result, output_json)

    verdict = result_detail.get("verdict", "Unknown")
    print(f"Verdict: {verdict} ({args.label_a} perspective: Win/Lose/Tie)")
    print(f"JSON saved to: {output_json}")
    print(f"CSV saved to:  {csv_path}")
    return 0 if verdict != "Error" else 1


if __name__ == "__main__":
    sys.exit(main())
