# Written by Yukang Chen
# Core code based on https://github.com/CStanKonrad/long_llama
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import math
import torch
import argparse
import random
import wonderwords
import numpy as np
from numpy import random
from tqdm import tqdm
import transformers
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
# from llama_attn_replace import replace_llama_attn

# Words
nouns = wonderwords.random_word._get_words_from_text_file("nounlist.txt")
adjs = wonderwords.random_word._get_words_from_text_file("adjectivelist.txt")
# verbs = wonderwords.random_word._get_words_from_text_file("verblist.txt")
words = [f"{adj}-{noun}" for adj in adjs for noun in nouns]
words = sorted(list(set(words)))

def parse_config():
    parser = argparse.ArgumentParser(description='arg parser')
    parser.add_argument('--base_model', type=str, default="/data1/pretrained-models/llama-7b-hf")
    parser.add_argument('--cache_dir', type=str, default="./cache")
    parser.add_argument('--context_size', type=int, default=-1, help='context size during fine-tuning')
    parser.add_argument('--flash_attn', type=bool, default=True, help='whether to use flash attention 2')
    parser.add_argument('--max_tokens', type=int, default=32000, help='maximum token length for evaluation')
    parser.add_argument('--interval', type=int, default=1000, help='interval for evaluation')
    parser.add_argument('--num_tests', type=int, default=10, help='number of repeat testing for each length')
    parser.add_argument('--attn_mlp_checkpoint_path', type=str, default=None, help='path to the checkpoint of the attention MLP')
    parser.add_argument('--finetune_checkpoint_path', type=str, default=None, help='path to the checkpoint of the finetuned model')

    args = parser.parse_args()
    return args


def generate_prompt_landmark(n_garbage, seed):
    """Generates a text file and inserts an passkey at a random position."""
    rnd_state = random.get_state()
    random.seed(seed)
    n_garbage_prefix = random.randint(0, n_garbage)
    n_garbage_suffix = n_garbage - n_garbage_prefix

    task_description = "There is an important info hidden inside a lot of irrelevant text. Find it and memorize them. I will quiz you about the important information there."
    garbage = "The grass is green. The sky is blue. The sun is yellow. Here we go. There and back again."
    ### For NIAH1
    # task_description = "A special magic number is hidden within the following text. Make sure to memorize it. I will quiz you about the number afterwards."
    # garbage = "The grass is green. The sky is blue. The sun is yellow. Here we go. There and back again.\n"
    garbage_inf = " ".join([garbage] * 5000)
    assert len(garbage_inf) >= n_garbage
    garbage_prefix = garbage_inf[:n_garbage_prefix]
    garbage_suffix = garbage_inf[:n_garbage_suffix]
    pass_key = random.randint(1, 50000)
    # pass_key = random.randint(1000000, 10000000) # For NIAH1
    information_line = f"The pass key is {pass_key}. Remember it. {pass_key} is the pass key."
    final_question = "What is the pass key? The pass key is"
    ### For NIAH1
    # word_key = random.choice(words)
    # print("word_key", word_key)
    # information_line = f"One of the special magic numbers for {word_key} is {pass_key}."
    # information_line = f"One of the special magic numbers for {word_key} is {pass_key}. Remember it. {pass_key} is the magic numbers for {word_key}."
    # final_question = f"What is the special magic number for {word_key} mentioned in the provided text? The special magic number for {word_key} mentioned in the provided text is"
    lines = [
        task_description,
        garbage_prefix,
        information_line,
        garbage_suffix,
        final_question,
    ]
    random.set_state(rnd_state)
    return "\n".join(lines), str(pass_key), n_garbage_prefix


def passkey_retrieval_test(model, tokenizer, device, use_cache=False, n_garbage=60000, seed=666, output_attentions=False, total_num_tests=10):
    prompt, answer, n_garbage_prefix = generate_prompt_landmark(n_garbage, seed)
    tok = tokenizer(prompt, return_tensors="pt").to(device)
    input_ids = tok.input_ids
    attention_mask = tok.attention_mask
    input_ids = input_ids.to(device)
    len_token = input_ids.shape[-1]
    answer_ids = tokenizer(answer, return_tensors="pt").input_ids[:, 1:] # drop BOS
    generation_output = model.generate(
        input_ids=input_ids, attention_mask=attention_mask, output_attentions=output_attentions,
        max_new_tokens=answer_ids.shape[-1]+1, num_beams=1, use_cache=use_cache,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        do_sample=False,
    )
    model_answer = generation_output[0, -answer_ids.shape[-1]:].cpu() # 
    # is_correct = (model_answer == answer_ids[0]).all().item()
    ori_answer = tokenizer.decode(answer_ids[0].cpu())
    ori_model_answer = tokenizer.decode(model_answer.cpu())
    is_correct = (ori_answer in ori_model_answer)
    if total_num_tests < 20:
        print(f"The correct answer is {tokenizer.decode(answer_ids[0].cpu())}, total tokens: {len_token}, n_garbage: {n_garbage}, n_garbage_prefix: {n_garbage_prefix}")
        print(f"The model answer is {tokenizer.decode(model_answer.cpu())}, is_correct : {is_correct}")
    if output_attentions:
        breakpoint()
    return is_correct, len_token


def main(args):
    device = "cuda:0"
    torch.cuda.set_device(device)

    # print("base model", args.base_model)

    # if args.flash_attn:
    #     replace_llama_attn(use_full=True)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(project_root)
    from src.model.load_model_for_eval import load_model_from_checkpoint, load_model_from_config
    
    attn_mlp_checkpoint_path = args.attn_mlp_checkpoint_path
    finetune_checkpoint_path = args.finetune_checkpoint_path
    model, config, tokenizer = load_model_from_checkpoint(
                                            attn_mlp_checkpoint_path=attn_mlp_checkpoint_path,
                                            finetune_checkpoint_path=finetune_checkpoint_path,
                                            config_dir='./configs',
                                            print_model=False,
                                            debug=False,
                                            lm_eval_model=False,
                                            # path_to_lm_eval_harness=LM_EVALUATION_HARNESS_PATH,
                                        )

    print(model)
    print(config)
    # print(tokenizer)
    model = model.to(device)
    # Set RoPE scaling factor
    context_size = args.context_size
    orig_ctx_len = getattr(config, "max_position_embeddings", None) # this value should be 4096 for LLaMA2 models
    print('check orig_ctx_len', orig_ctx_len, 'context_size', context_size, len(tokenizer))

    total_test_points = args.max_tokens // args.interval
    all_accuries = {}
    for i in range(total_test_points):
        # This is a rough ratio to control the number of texts and tokens
        n_garbage = int(3.75 * (i + 1) * args.interval // 1024 * 1024)
        passed_tests = 0
        total_tokens = 0
        output_attentions = False
        # if i == 0:
        #     output_attentions = True
        for i in range(args.num_tests): # use_cache=not args.flash_attn
            is_correct, len_tokens = passkey_retrieval_test(model, tokenizer, device, use_cache=True, n_garbage=n_garbage, seed=i, output_attentions=output_attentions, total_num_tests=args.num_tests)
            passed_tests += is_correct
            total_tokens += len_tokens
        avg_tokens = total_tokens//args.num_tests
        accuracy = float(passed_tests)/args.num_tests
        print("accuracy on the token length %d is %f"%(avg_tokens, accuracy))
        all_accuries[str(avg_tokens)] = accuracy
    print("accuries over tokens", all_accuries)


if __name__ == "__main__":
    args = parse_config()
    main(args)