"""Model collection from HuggingFace Hub."""
from huggingface_hub import HfApi
from config import CONFIG


def fetch_vit_model_ids(n_fetch: int = None) -> list[str]:
    """Fetch ViT model IDs from HuggingFace Hub."""
    n_fetch = n_fetch or CONFIG.n_models_fetch
    api = HfApi()
    models = list(api.list_models(
        filter=CONFIG.pipeline_tag,
        search=CONFIG.search_query,
        sort="downloads",
        direction=-1,
        limit=n_fetch
    ))
    return [m.modelId for m in models]


if __name__ == "__main__":
    ids = fetch_vit_model_ids(10)
    print(f"Fetched {len(ids)} models: {ids[:5]}...")
