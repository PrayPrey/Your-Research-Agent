from dataclasses import dataclass, field
from typing import List


@dataclass
class AuditConfig:
    llm_lb_url: str = "https://github.com/fboulnois/llm-leaderboard-csv/releases/download/v1.3.0/llm.csv"
    llm_lb_cache: str = "./data/llm_leaderboard_v1/llm.csv"
    bbq_cache: str = "./data/bbq_scores/bbq_per_model.csv"
    helm_lite_dataset: str = "stanford-crfm/helm-lite"

    fuzzy_threshold: int = 75
    fuzzy_processor: str = "default_process"
    fallback_thresholds: List[int] = field(default_factory=lambda: [70, 65])
    fallback_scorer: str = "token_set_ratio"
    match_rate_fallback_trigger: float = 0.55

    n_complete_min: int = 30
    match_rate_min: float = 0.55

    figures_dir: str = "./docs/youra_research/h-e1/figures"
    save_csv: bool = True

    sensitivity_thresholds: List[int] = field(default_factory=lambda: [65, 70, 75, 80])

    seed: int = 42


def load_config(yaml_path: str = None) -> AuditConfig:
    if yaml_path is None:
        return AuditConfig()
    import yaml
    with open(yaml_path) as f:
        raw = yaml.safe_load(f)
    d = raw.get("data", {})
    fz = raw.get("fuzzy", {})
    g = raw.get("gate", {})
    o = raw.get("output", {})
    s = raw.get("sensitivity", {})
    return AuditConfig(
        llm_lb_url=d.get("llm_lb_url", AuditConfig.llm_lb_url),
        llm_lb_cache=d.get("llm_lb_cache", AuditConfig.llm_lb_cache),
        bbq_cache=d.get("bbq_cache", AuditConfig.bbq_cache),
        helm_lite_dataset=d.get("helm_lite_dataset", AuditConfig.helm_lite_dataset),
        fuzzy_threshold=fz.get("threshold", AuditConfig.fuzzy_threshold),
        fuzzy_processor=fz.get("processor", AuditConfig.fuzzy_processor),
        fallback_thresholds=fz.get("fallback_thresholds", [70, 65]),
        fallback_scorer=fz.get("fallback_scorer", AuditConfig.fallback_scorer),
        match_rate_fallback_trigger=fz.get("match_rate_fallback_trigger", AuditConfig.match_rate_fallback_trigger),
        n_complete_min=g.get("n_complete_min", AuditConfig.n_complete_min),
        match_rate_min=g.get("match_rate_min", AuditConfig.match_rate_min),
        figures_dir=o.get("figures_dir", AuditConfig.figures_dir),
        save_csv=o.get("save_csv", AuditConfig.save_csv),
        sensitivity_thresholds=s.get("thresholds", [65, 70, 75, 80]),
        seed=raw.get("seed", AuditConfig.seed),
    )
