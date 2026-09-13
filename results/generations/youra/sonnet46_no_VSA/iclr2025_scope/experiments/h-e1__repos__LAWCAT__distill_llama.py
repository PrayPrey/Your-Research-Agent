"""
Script to distill pretrained Transformers into linear attention variants
"""
import sys
import os
from os.path import join

import argparse
import torch
from omegaconf import OmegaConf

sys.path.append('./src')
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = 'true'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from utils.setup import (
    init_wandb, seed_everything, flatten_config, get_run_name_from_args,
    update_config_from_args, update_model_config_from_args,
)
from utils.logging import print_config, print_header
from utils.global_vars import get_global_args, set_global_args, set_global_count

from dataloaders import load_data
from trainer import get_trainer, get_optimizer, get_scheduler
from finetune import prepare_finetune_configs, get_finetuner

from model.pretrained import get_pretrained_loader
from model.load_model import load_and_convert_attns, load_and_convert_finetune
from model.convert_model import toggle_attention, remove_base_attention
from model.utils import count_parameters


def get_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_name", type=str, default='LAWCAT')
    parser.add_argument("--model_config", type=str, default=None)
    parser.add_argument("--distill_config", type=str, default=None)
    parser.add_argument("--finetune_config", type=str, default=None)
    parser.add_argument("--eval_config", type=str, default=None)

    parser.add_argument("--pretrained_model_name_or_path", type=str, default=None)
    parser.add_argument("--load_distill_checkpoint", type=str, default=None)
    parser.add_argument("--resume_distill", action='store_true', default=None)
    
    parser.add_argument("--load_finetune_checkpoint", type=str, default=None)
    parser.add_argument("--resume_finetune", action='store_true', default=None)

    # Override default configs
    # Feature map / model
    parser.add_argument("--attention_type", type=str, default=None)
    parser.add_argument("--learned_kernel", type=str, default=None)  # always
    parser.add_argument("--lk_skip_connection", action='store_true', default=None)
    parser.add_argument("--lk_zero_init", action='store_true', default=None)
    parser.add_argument("--lk_normal_init", action='store_true', default=None)
    parser.add_argument("--tie_qk_kernels", action='store_true', default=None)
    parser.add_argument("--train_qk", action='store_true', default=None)
    parser.add_argument("--state_chunk_len", type=int, default=None)
    parser.add_argument("--window_size", type=int, default=None)
    parser.add_argument("--sink_size", type=int, default=None)
    
    # Training
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--weight_decay", type=float, default=None)
    parser.add_argument("--optim", type=str, default=None)
    parser.add_argument("--scheduler", type=str, default=None)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=None)
    parser.add_argument("--num_train_epochs", type=int, default=None)
    parser.add_argument("--max_steps", type=int, default=None)
    parser.add_argument("--max_finetune_steps", type=int, default=None)

    parser.add_argument("--no_peft_grad_ckpt", action='store_true', default=None)
    
    # Dataloading
    parser.add_argument("--batch_size", type=int, default=None)
    parser.add_argument("--num_workers", type=int, default=None)

    # Evaluation
    parser.add_argument("--no_init_eval", action='store_true', default=False)
    parser.add_argument("--eval_steps", type=int, default=None)
    parser.add_argument("--max_eval_batches", type=int, default=None)

    # Miscellaneous
    parser.add_argument("--huggingface_token", type=str, default=None)
    parser.add_argument("--checkpoint_dir", type=str, default='/home/liuzeyu/LAWCAT/ckp')
    parser.add_argument("--results_dir", type=str, default='/home/liuzeyu/LAWCAT/results')
    parser.add_argument("--replicate", type=int, default=0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--verbose", action='store_true', default=None)
    parser.add_argument("--no_cuda", action='store_true', default=None)
    parser.add_argument("--no_wandb", action='store_true', default=None)
    # parser.add_argument("--wandb_entity", type=str, default='hazy-research')
    parser.add_argument("--debug", action='store_true', default=None)
    parser.add_argument("--no_attention_mask", action='store_true', default=None)

    args = parser.parse_args()
    args.run_name = get_run_name_from_args(args)
    return args


def main():
    # ------
    # SET UP
    # ------
    args = get_args()
    args.checkpoint_dir = join(args.checkpoint_dir, args.model_config)
    if not os.path.isdir(args.checkpoint_dir):
        os.makedirs(args.checkpoint_dir)
    args.results_dir = join(args.results_dir, args.model_config)
    if not os.path.isdir(args.results_dir):
        os.makedirs(args.results_dir)
    seed_everything(args.seed)
    args.device = torch.device('cuda')

    # Load distillation + attention configs
    distill_config_path = join('./configs/experiment', f'{args.distill_config}.yaml')
    distill_config = OmegaConf.load(distill_config_path)
    distill_config = update_config_from_args(distill_config, args)

    model_config_path = join('./configs/model', f'{args.model_config}.yaml')
    model_config = OmegaConf.load(model_config_path)
    model_config = update_model_config_from_args(model_config, args)

    args.run_name = args.run_name.replace('True', '1').replace('False', '0')  # concise hacks
        
    # Update data tokenizer to match model
    for k in ['pretrained_model_name_or_path', 'cache_dir']:
        distill_config.dataset.pretrained_model_config[k] = model_config.model[k]

    # Update optimizer if specified
    if 'optimizer' in model_config:
        for k, v in model_config.optimizer.items():
            distill_config.optimizer[k] = v

    print_header('Distillation Config')
    print_config(distill_config)
    print_header('Model Config')
    print_config(model_config)
    set_global_args(model_config)

    # WandB logging
    if args.no_wandb:
        wandb = None
    else:
        wandb = init_wandb(args)
    if wandb is not None:
        distill_config['model'] = model_config  # Combine for logging
        _flattened = {'model': model_config,
                      'model_config': args.model_config,  # config file names
                      'distill_config': args.distill_config,
                      'finetune_config': args.finetune_config,
                      'distill_checkpoint': args.load_distill_checkpoint,
                      'finetune_checkpoint': args.load_finetune_checkpoint,
                      'replicate': args.replicate}
        flatten_config(OmegaConf.to_container(distill_config), _flattened, '')
        wandb.config.update(_flattened)

    # Get pretrained model
    model_loader = get_pretrained_loader(**model_config.model,
                                         huggingface_token=args.huggingface_token)
    tokenizer = model_loader.load_tokenizer()
    tokenizer.pad_token_id = tokenizer.eos_token_id
    tokenizer.padding_side = 'left'

    # Convert model
    try:
        args.attention_type = model_config['attention']['attention_type']
    except AttributeError:
        args.attention_type = 'lolcats_llama'
    model = model_loader.load(model_type=args.attention_type)
    model.state_chunk_len = model_config['attention']['state_chunk_len']

    if args.verbose:
        print_header('*** Initial Model ***')
        print(model)

    # --------
    # TRAINING
    # --------
    # 1. Distill attentions
    train_loader = None
    finetune_only = model_config['attention'].get('finetune_only', False)
    if not finetune_only and (args.load_distill_checkpoint is None or args.resume_distill):
        if args.resume_distill:
            checkpoint_path = args.load_distill_checkpoint
        else:
            checkpoint_path = None
        # Swap initial attentions if applicable
        softmax_attns = model_config['attention'].get('softmax_attentions', [])
        model, distill_peft_config = load_and_convert_attns(model, model_config, 
                                                            attention_type=args.attention_type, 
                                                            checkpoint_path=checkpoint_path, 
                                                            print_model=args.verbose,
                                                            merge_loras=False,
                                                            peft_gradient_checkpointing=not args.no_peft_grad_ckpt,
                                                            train_attention=True)
        if hasattr(distill_config.trainer, 'train_gumbel_gate') and not distill_config.trainer.train_gumbel_gate: # 16778432 -> 16778240
            for n, p in model.named_parameters():
                if 'window_diff_mask' in n:
                    p.requires_grad = False
        if distill_config.trainer.name is not None:  # Get data for distilling
            dataloaders  = load_data(distill_config.dataset, distill_config.dataloader)
            try:
                train_loader = dataloaders[distill_config.trainer.train_split] # 9428 [1, state_chunk_len]
                eval_loader  = dataloaders[distill_config.trainer.val_split] # 32
            except:
                train_loader = dataloaders['train']
                eval_loader  = dataloaders['validation']
            total_distll_steps = int(len(train_loader) * distill_config.trainer.num_train_epochs / distill_config.trainer.gradient_accumulation_steps)
            if distill_config.lr_scheduler.lr_scheduler_type == 'cosine_warmup':
                distill_config.lr_scheduler.num_warmup_steps = total_distll_steps // 100
                distill_config.lr_scheduler.num_training_steps = total_distll_steps
                print(f'-> Warmup steps: {distill_config.lr_scheduler.num_warmup_steps}, Total steps: {distill_config.lr_scheduler.num_training_steps} \
                      len(train_loader): {len(train_loader)}, num_train_epochs: {distill_config.trainer.num_train_epochs}, gradient_accumulation_steps: {distill_config.trainer.gradient_accumulation_steps}')
            if args.verbose:
                print_header('*** Dataset preview ***')
                for ix, data in enumerate(train_loader):
                    print('-> Train data input_ids.shape:', data['input_ids'].shape)
                    break
                for ix, data in enumerate(eval_loader):
                    print('-> Eval  data input_ids.shape:', data['input_ids'].shape)
                    break
                
                for ix, data in enumerate(dataloaders[distill_config.trainer.val_split]):
                    print('-> Prompt:')
                    print(tokenizer.batch_decode(data['input_ids'])[0])
                    if 'position_ids' in data:
                        print('-> Position IDs:')
                        print('shape:', data['position_ids'].shape)
                        print(data['position_ids'])
                    break
        
            # Log some stats
            distill_config.model_train_params = count_parameters(model, requires_grad=True)
            distill_config.model_total_params = count_parameters(model, requires_grad=False)
            pct_trainable = distill_config.model_train_params / distill_config.model_total_params
        
            print_header('*** Distillation Parameter Counts ***')
            print(f'├── Number training to distill:  {distill_config.model_train_params}')
            print(f'├── Number of total parameters:  {distill_config.model_total_params}')
            print(f'├── Percent training to distill: {pct_trainable * 100:.3f}%')
         
            # Get optimizer and scheduler
            optimizer = get_optimizer(model=model, **distill_config.optimizer)
            scheduler = get_scheduler(optimizer=optimizer, **distill_config.lr_scheduler)
        
            # Load trainer 
            for arg, argv in distill_config.trainer.items():
                if arg != 'name':
                    setattr(args, arg, argv)
            for _config in ['dataloader', 'optimizer', 'lr_scheduler']:
                setattr(args, _config, OmegaConf.to_container(getattr(distill_config, _config)))

            OurTrainer = get_trainer(distill_config.trainer.name)
            trainer = OurTrainer(model=model,
                                 args=args,
                                 lr_scheduler_args=distill_config.lr_scheduler,
                                 train_loader=train_loader,
                                 eval_loader=eval_loader,
                                 optimizer_and_scheduler=(optimizer, scheduler),
                                 device=args.device,
                                 wandb=wandb,
                                 checkpoint_suffix='_distill',
                                 save_results=False,
                                 **distill_config.trainer)

            # Train / distill model
            print_header('*** Distilling Attentions ***')
            print(f'├── Experiment name: {args.run_name}')
            print(f'├── Device: {args.device}')
            print(f'├── Seed: {args.seed}')
            model = toggle_attention(model, train=True, softmax_attns=softmax_attns)
            model = trainer.train(mode='distill')

            # Prepare for downstream finetune / eval
            model = toggle_attention(model, train=False, softmax_attns=softmax_attns)
            model = remove_base_attention(model, softmax_attns=softmax_attns)
            if ('peft_config' in model_config['attention'] or 'peft' in model_config['attention']):
                model = model.merge_and_unload()

            args.load_distill_checkpoint = trainer.best_val_checkpoint_path
        else:
            print('-> No distillation')
            total_distll_steps = 0
            try:
                model = toggle_attention(model, train=False, softmax_attns=softmax_attns)
            except:
                pass
    else:  # i.e., args.load_distill_checkpoint is not None:
        total_distll_steps = 0
        if args.load_distill_checkpoint == 'default':  # lazy identifier
            checkpoint_path = f'{join(args.checkpoint_dir, args.run_name)}_distill.pt'
        else:
            checkpoint_path = args.load_distill_checkpoint
        
        # If we distill with LoRA
        merge_loras=('peft_config' in model_config['attention'] or
                     'peft' in model_config['attention'])
        softmax_attns = model_config['attention'].get('softmax_attentions', [])
        model, distill_peft_config = load_and_convert_attns(model, model_config, 
                                                            attention_type=args.attention_type, 
                                                            checkpoint_path=checkpoint_path,
                                                            print_model=args.verbose, 
                                                            merge_loras=merge_loras,
                                                            train_converted=False,
                                                            peft_gradient_checkpointing=not args.no_peft_grad_ckpt,
                                                            train_attention=False)
        model = toggle_attention(model, train=False, softmax_attns=softmax_attns)
        model = remove_base_attention(model, softmax_attns=softmax_attns)

    if distill_peft_config is not None and wandb is not None:
        _flattened['peft_distill'] = distill_peft_config
        wandb.config.update(_flattened)

    # 2. Finetune model further (if desired)
    torch.cuda.empty_cache()
    torch.cuda.synchronize() 
    if (args.finetune_config is not None or
        (args.load_finetune_checkpoint is not None and args.resume_finetune)):
        # TODO: This is the generation evaluation, should fix later
        if not args.no_init_eval:
            print_header('*** Distilled Evaluation ***')
            print('model config: ', model.config)
            initial_metrics = evaluate_model(model, tokenizer)
            for k, v in initial_metrics.items():
                print(f'├── {k}: {v}')

        if args.max_finetune_steps is not None:
            args.max_steps = args.max_finetune_steps
        if args.load_finetune_checkpoint is None or args.resume_finetune:
            finetune_config, args = prepare_finetune_configs(args, model_config,
                                                             args.finetune_config)
            # For now, don't train any softmax attention layers
            if 'softmax_attentions' in model_config['attention']:
                finetune_config['finetune']['layers_to_ignore'] = model_config['attention']['softmax_attentions']
            checkpoint_path = args.load_finetune_checkpoint
            print('before load_and_convert_finetune: ', model.config)
            model, ft_peft_config = load_and_convert_finetune(model, finetune_config, 
                                                              checkpoint_path=checkpoint_path,
                                                              print_model=args.verbose,
                                                              merge_loras=False,
                                                              peft_gradient_checkpointing=not args.no_peft_grad_ckpt)
            print('after load_and_convert_finetune: ', model.config)
            if args.verbose:
                print_header(f'*** Trainable finetuning parameters ***')
                for n, p in model.named_parameters():
                    if p.requires_grad:
                        print(f'├── {n} ({p.dtype})')
                
            finetune_trainer = get_finetuner(model, finetune_config, args.device, args, wandb)
            if args.verbose:
                print_header('Finetune config')
                print_config(finetune_config)
            print_header('*** Finetuning ***')
            print(f'├── Experiment name: {args.run_name}')
            print(f'├── Device: {args.device}')
            print(f'├── Seed: {args.seed}')
            model = finetune_trainer.train(mode='finetune', init_step=total_distll_steps)
            args.load_finetune_checkpoint = finetune_trainer.best_val_checkpoint_path
        else:
            finetune_config, args = prepare_finetune_configs(args, model_config,
                                                             finetune_config_name=None,
                                                             finetune_checkpoint_name=args.load_finetune_checkpoint)
            model, ft_peft_config = load_and_convert_finetune(model, finetune_config, 
                                                              args.load_finetune_checkpoint,
                                                              print_model=args.verbose,
                                                              merge_loras=True,
                                                              peft_gradient_checkpointing=not args.no_peft_grad_ckpt)
            print(f'-> Finetuned checkpoint loaded from {args.load_finetune_checkpoint}!')

        if ft_peft_config is not None and wandb is not None:
            _flattened['peft_ft'] = ft_peft_config
            try:
                wandb.config.update(_flattened, allow_val_change=True)
            except:
                print('-> Failed to update WandB config')

    if not args.no_init_eval:  # Check on summary example
        print_header('*** Distilled + Finetuned Evaluation ***')
        initial_metrics = evaluate_model(model, tokenizer)
        for k, v in initial_metrics.items():
            print(f'├── {k}: {v}')

    if args.eval_config is not None:
        eval_config = OmegaConf.load(join('./configs/experiment', f'{args.eval_config}.yaml'))
        # Update data tokenizer to match model
        for k in ['pretrained_model_name_or_path', 'cache_dir']:
            eval_config.dataset.pretrained_model_config[k] = model_config['model'][k]
        for arg, argv in eval_config.trainer.items():
            if arg != 'name':
                setattr(args, arg, argv)
        finetune_trainer = get_evaluator(model, eval_config, args, args.device, wandb)

    # Final eval
    if 'save10' not in args.distill_config and 'save10' not in args.finetune_config:
        print_header('*** Distilled + Finetuned Final Eval ***')
        final_metrics = finetune_trainer.evaluate(model, step=-1, max_batches=None, prefix='final')  
        print_header('*** Saved Checkpoints ***')
        print(f'--attn_mlp_checkpoint_path {args.load_distill_checkpoint} \\')
        print(f'--finetune_checkpoint_path {args.load_finetune_checkpoint} \\')
        # print(f'--finetune_long_checkpoint_path {args.load_finetune_long_checkpoint} \\')
    
        print(final_metrics)
        for k, v in final_metrics.items():
            print(f'├── {k}: {v:.4f}')
        if wandb is not None:
            wandb.log({f'final/{k}': v for k, v in final_metrics.items()})


# ------------------
# Evaluation helpers
# ------------------

def get_evaluator(model, eval_config, args, device, wandb):
    """
    Get final evaluator class
    """
    dataloaders = load_data(eval_config.dataset, eval_config.dataloader)
    eval_loader = (dataloaders['test'] if 'test' in dataloaders else 
                   dataloaders[eval_config.trainer.val_split])
    OurTrainer = get_trainer(eval_config.trainer.name)        
    trainer = OurTrainer(model=model,
                         args=args,
                         train_loader=eval_loader,
                         eval_loader=eval_loader,
                         optimizer_and_scheduler=(None, None),
                         device=device,
                         wandb=wandb,
                         checkpoint_suffix='_final',
                         **eval_config.trainer)
    return trainer


def evaluate_model(model, tokenizer):
    """Coherence check using a SamSUM sample"""
    model.eval()
    # model.to(device)
    with torch.no_grad():
        model_input = tokenizer(SAMPLE_PROMPT, return_tensors="pt").to(model.device)
        print(tokenizer.decode(model.generate(**model_input, 
                                              # use_cache=False,
                                              max_new_tokens=100)[0],
                               skip_special_tokens=True))
    return {}

if __name__ == '__main__':
    main()
