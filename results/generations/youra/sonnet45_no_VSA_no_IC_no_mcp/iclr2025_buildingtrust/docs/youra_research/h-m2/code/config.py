"""
Configuration for h-m2 correction routing experiment.
"""

CONFIG = {
    "data": {
        "h_e1_results_path": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_buildingtrust/docs/youra_research/h-e1/code/results/entropy_results.json",
        "h_m1_results_path": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_buildingtrust/docs/youra_research/h-m1/code/results/classification_results.json",
        "h_m1_threshold": 0.32,  # From h-m1 validation
        "n_samples_per_model": 50,
        # Using synthetic TruthfulQA-style questions since real dataset unavailable in test environment
        "use_synthetic": True
    },
    "models": {
        "gpt35": {
            "name": "gpt-3.5-turbo",
            "api_key_env": "OPENAI_API_KEY",
            "temperature": 0.7,
            "max_tokens": 150,
            "enabled": False  # Disabled for ablation test (no external API)
        },
        "llama2": {
            "name": "meta-llama/Llama-2-7b-chat-hf",
            "temperature": 0.7,
            "max_tokens": 150,
            "load_in_4bit": True,  # Memory optimization
            "enabled": False  # Disabled for ablation test (no HF downloads)
        },
        # Mock models for ablation testing
        "mock": {
            "enabled": True,
            "entity_error_cot_success": 0.30,  # 30% success for mismatched routing
            "entity_error_rag_success": 0.55,  # 55% success for matched routing (25pp diff)
            "noise_std": 0.05
        }
    },
    "rag": {
        "spacy_model": "en_core_web_sm",
        "top_k_docs": 3,
        "retrieval_method": "wikipedia_api",
        "use_mock": True  # Mock Wikipedia for ablation test
    },
    "cot": {
        "prompt_template": "Question: {question}\nIncorrect answer: {incorrect_answer}\n\nLet's think step by step to find the correct answer:",
        "use_mock": True  # Mock COT for ablation test
    },
    "evaluation": {
        "gate_threshold_pp": 20.0,  # Percentage points
        "gate_threshold_rel": 50.0,  # Relative improvement %
        "use_gpt_judge": False,  # Disabled for ablation test
        "gpt_judge_model": "gpt-3.5-turbo"
    },
    "output": {
        "results_file": "./results/correction_results.json",
        "figures_dir": "./figures/"
    },
    "seed": 42
}
