from tape import training

TRAIN_ARGS = {
    'model_type': 'transformer',
    'task': 'secondary_structure',
    'learning_rate': 0.0001,
    'batch_size': 4,
    'num_train_epochs': 1,
    'num_log_iter': 2,
    'fp16': False,
    'warmup_steps': 10,
    'gradient_accumulation_steps': 1,
    'loss_scale': 0,
    'max_grad_norm': 1.0,
    'exp_name': None,
    'from_pretrained': None,
    'log_dir': './logs',
    'eval_freq': 1,
    'save_freq': 1,
    'model_config_file': None,
    'data_dir': './data',
    'output_dir': './results',
    'no_cuda': True,
    'seed': 42,
    'local_rank': -1,
    'tokenizer': 'iupac',
    'num_workers': 1,
    'debug': True,
    'log_level': 'DEBUG',
    'patience': -1,
    'resume_from_checkpoint': False
}

if __name__ == '__main__':
    training.run_train(**TRAIN_ARGS)
