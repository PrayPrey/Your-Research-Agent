import logging
import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import ExperimentConfig
from data.longbench_loader import load_task
from eviction.score_functions import score_M1, score_M2, score_M6
from eviction.eviction import apply_kv_eviction
from evaluation.metrics import compute_f1

logger = logging.getLogger(__name__)

# Store spot-check scores for Figure 4
_spot_check_scores = {"M1": [], "M2": []}


def _capture_attn_scores_via_hook(model, method: str, seq_len: int, cfg: ExperimentConfig):
    """
    Register forward hooks on each attention layer to compute importance scores
    in-place during forward and discard the full (B, H, S, S) attention matrix.

    Must call model(..., output_attentions=True) to trigger attention weight computation.
    Hook fires per-layer sequentially — peak VRAM overhead ~1GB (one layer at a time).

    Returns (hook_handles, scores_buffer) where scores_buffer[l] = (B, H, S) score tensor.
    """
    scores_buffer = {}
    handles = []

    def _make_hook(layer_idx: int):
        def hook_fn(module, input, output):
            if not isinstance(output, tuple) or len(output) < 2:
                return
            attn_weights = output[1]
            if attn_weights is None:
                return
            # attn_weights: (B, H, S, S) — compute score, discard full matrix
            attn_f32 = attn_weights.float()
            if method == "M1":
                w = min(cfg.observation_window, attn_f32.shape[2])
                sc = attn_f32[:, :, -w:, :].mean(dim=2)  # (B, H, S)
            elif method == "M2":
                sc = attn_f32.sum(dim=2)  # (B, H, S)
            else:
                return
            scores_buffer[layer_idx] = sc.detach()
            del attn_f32
        return hook_fn

    # Match LLaMA attention modules: LlamaAttention, LlamaEagerAttention, etc.
    for name, module in model.named_modules():
        cls_name = type(module).__name__
        if "Attention" in cls_name and hasattr(module, "head_dim"):
            layer_idx = len(handles)
            h = module.register_forward_hook(_make_hook(layer_idx))
            handles.append(h)

    return handles, scores_buffer


def _remove_hooks(handles: list):
    for h in handles:
        h.remove()


def _greedy_decode(model, tokenizer, start_token_ids: torch.Tensor, past_kv, max_new_tokens: int) -> str:
    """Manual greedy decode — compatible with transformers 5.x DynamicCache."""
    eos_id = tokenizer.eos_token_id
    next_tok = start_token_ids  # (1, 1)
    kv = past_kv
    generated = []

    for _ in range(max_new_tokens):
        with torch.no_grad():
            step_out = model(next_tok, past_key_values=kv, use_cache=True)
        logits = step_out.logits[:, -1, :]
        next_tok = logits.argmax(dim=-1, keepdim=True)  # (1, 1)
        kv = step_out.past_key_values
        tok_id = next_tok.item()
        if tok_id == eos_id:
            break
        generated.append(tok_id)

    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def run_single_example(
    example: dict,
    method: str,
    model,
    tokenizer,
    cfg: ExperimentConfig,
    store_spot_check: bool = False,
) -> str:
    input_ids = example["input_ids"].to(model.device)
    seq_len = input_ids.shape[1]

    need_attn = (method in ("M1", "M2"))

    if need_attn:
        # Hook-based attention capture: compute scores in-place per layer during forward.
        # Passes output_attentions=True to trigger weight computation per layer.
        # Peak VRAM overhead ~1GB (one layer processed at a time, hook discards immediately).
        handles, scores_buffer = _capture_attn_scores_via_hook(model, method, seq_len, cfg)

    with torch.no_grad():
        outputs = model(input_ids, use_cache=True, output_attentions=need_attn)

    past_kv = outputs.past_key_values

    if need_attn:
        _remove_hooks(handles)
        # Convert scores_buffer dict to ordered list
        n_layers = len(list(past_kv))
        scores = [scores_buffer.get(l, None) for l in range(n_layers)]
        # Fallback: if hook didn't capture (model-specific), use M2 sum of 1s (uniform)
        for l in range(n_layers):
            if scores[l] is None:
                logger.warning(f"Layer {l}: attention hook returned nothing — falling back to uniform scores")
                S = list(past_kv)[l][0].shape[2]
                scores[l] = torch.ones(1, 1, S, device=model.device)
    elif method == "M6":
        keep_n = int(seq_len * cfg.retention_ratio)
        scores = [score_M6(seq_len, keep_n, cfg.streaming_sink_size).to(model.device) for _ in range(32)]
    else:  # M0
        scores = None

    torch.cuda.empty_cache()

    if method != "M0":
        evicted_kv = apply_kv_eviction(
            past_kv, scores, cfg.retention_ratio, cfg.log_eviction_details
        )
        # Store spot-check scores for Figure 4
        if store_spot_check and method in ("M1", "M2") and len(_spot_check_scores[method]) < 5:
            s0 = scores[0].mean(dim=1).squeeze(0).cpu().float().numpy()
            _spot_check_scores[method].append(s0)
    else:
        evicted_kv = past_kv

    del scores, past_kv
    torch.cuda.empty_cache()

    # Manual greedy decode — works with transformers 5.x DynamicCache
    seed_token = input_ids[:, -1:]
    prediction = _greedy_decode(model, tokenizer, seed_token, evicted_kv, cfg.max_new_tokens)
    return prediction


def run_method(
    method: str,
    model,
    tokenizer,
    tasks_data: dict,
    cfg: ExperimentConfig,
) -> dict:
    results = {}
    for task_name, examples in tasks_data.items():
        f1_list = []
        store_spot = (method in ("M1", "M2"))
        for i, ex in enumerate(tqdm(examples, desc=f"{method}/{task_name}")):
            try:
                pred = run_single_example(
                    ex, method, model, tokenizer, cfg,
                    store_spot_check=(store_spot and i < 5)
                )
                f1 = compute_f1(pred, ex["answers"], task_name)
            except Exception as e:
                logger.warning(f"Example {i} failed ({method}/{task_name}): {e}")
                import traceback
                logger.debug(traceback.format_exc())
                f1 = 0.0
            f1_list.append(f1)
        task_mean = sum(f1_list) / len(f1_list) if f1_list else 0.0
        results[task_name] = f1_list
        logger.info(f"{method}/{task_name} mean F1: {task_mean:.2f}")
    return results


def run_all(cfg: ExperimentConfig) -> tuple:
    import torch as _torch
    _torch.manual_seed(cfg.seed)

    logger.info(f"Loading model {cfg.model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # eager attn_implementation required for attention weight hooks
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_name,
        torch_dtype=_torch.float16,
        device_map=cfg.device_map,
        attn_implementation="eager",
    )
    model.eval()
    logger.info("Model loaded.")

    logger.info("Loading datasets...")
    tasks_data = {}
    for task in cfg.tasks:
        tasks_data[task] = load_task(
            task, tokenizer, cfg.examples_per_task, cfg.seed, cfg.max_context_length
        )
        logger.info(f"Loaded {len(tasks_data[task])} examples for {task}")

    raw_results = {}
    for method in cfg.methods:
        logger.info(f"=== Running method {method} ===")
        raw_results[method] = run_method(method, model, tokenizer, tasks_data, cfg)

    return raw_results, _spot_check_scores
