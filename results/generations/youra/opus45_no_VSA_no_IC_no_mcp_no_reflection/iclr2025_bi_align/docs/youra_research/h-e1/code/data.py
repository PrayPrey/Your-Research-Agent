"""H-E1 Data: IFEval loading + constraint parsing."""
import re
from datasets import load_dataset
from config import Config

CONSTRAINT_MAPPING = {
    "keywords:existence": ("keyword", True),
    "keywords:forbidden_words": ("keyword", False),
    "keywords:frequency": ("keyword_freq", None),
    "keywords:letter_frequency": ("letter_freq", None),
    "length_constraints:number_words": ("length_words", None),
    "length_constraints:number_sentences": ("length_sentences", None),
    "length_constraints:number_paragraphs": ("length_paragraphs", None),
    "length_constraints:nth_paragraph_first_word": ("structural", None),
    "detectable_content:number_placeholders": ("format", "placeholder"),
    "detectable_content:postscript": ("format", "postscript"),
    "detectable_format:number_bullet_lists": ("format", "bullet"),
    "detectable_format:constrained_response": ("format", "constrained"),
    "detectable_format:number_highlighted_sections": ("format", "highlight"),
    "detectable_format:multiple_sections": ("structural", "sections"),
    "detectable_format:json_format": ("format", "json"),
    "detectable_format:title": ("format", "title"),
    "change_case:english_capital": ("case", "capital"),
    "change_case:english_lowercase": ("case", "lowercase"),
    "combination:two_responses": ("structural", "two_responses"),
    "combination:repeat_prompt": ("structural", "repeat"),
    "startend:end_checker": ("startend", "end"),
    "startend:quotation": ("format", "quotation"),
    "punctuation:no_comma": ("punctuation", "no_comma"),
}


def load_ifeval(cfg: Config) -> list[dict]:
    """Load IFEval dataset."""
    ds = load_dataset(cfg.dataset_id, split=cfg.dataset_split)
    return list(ds)


def parse_constraints(example: dict) -> list[dict]:
    """Parse IFEval constraints into unified schema."""
    constraints = []
    instruction_ids = example.get("instruction_id_list", [])
    kwargs_list = example.get("kwargs", [])

    for i, instr_id in enumerate(instruction_ids):
        kwargs = kwargs_list[i] if i < len(kwargs_list) else {}
        c_type, c_subtype = CONSTRAINT_MAPPING.get(instr_id, ("unknown", None))

        constraint = {"type": c_type, "instruction_id": instr_id}

        if c_type == "keyword":
            keywords = kwargs.get("keywords", [])
            constraint["keywords"] = keywords
            constraint["must_include"] = c_subtype
        elif c_type == "length_words":
            constraint["type"] = "length"
            constraint["target"] = kwargs.get("num_words", 100)
            constraint["op"] = kwargs.get("relation", "at_least")
        elif c_type == "length_sentences":
            constraint["type"] = "length"
            constraint["unit"] = "sentences"
            constraint["target"] = kwargs.get("num_sentences", 3)
            constraint["op"] = kwargs.get("relation", "at_least")
        elif c_type == "length_paragraphs":
            constraint["type"] = "length"
            constraint["unit"] = "paragraphs"
            constraint["target"] = kwargs.get("num_paragraphs", 2)
            constraint["op"] = kwargs.get("relation", "at_least")
        elif c_type == "format":
            constraint["subtype"] = c_subtype
        elif c_type == "structural":
            constraint["subtype"] = c_subtype
        elif c_type == "case":
            constraint["case_type"] = c_subtype
        elif c_type == "startend":
            constraint["check"] = c_subtype
            constraint["end_phrase"] = kwargs.get("end_phrase", "")
        elif c_type == "punctuation":
            constraint["rule"] = c_subtype

        constraints.append(constraint)

    return constraints
