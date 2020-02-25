from tape import training

'''
DEFAULT_TRAIN_ARGS has the default train args which are injecting into training.run_train()
when you run `tape-train transformer secondary_structure`

They have been modified below in TRAIN_ARGS so that it is possible to run locally. The changes
that are definitely needed are setting no_cuda to True and batch_size to a lower number than
1024 (I arrived at 4 completely empirically). Lowering the number of epochs was just to get 
a successful training run quicker
'''

DEFAULT_TRAIN_ARGS = {
    'model_type': 'transformer',
    'task': 'secondary_structure',
    'learning_rate': 0.0001,
    'batch_size': 1024,
    'num_train_epochs': 10,
    'num_log_iter': 20,
    'fp16': False,
    'warmup_steps': 10000,
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
    'no_cuda': False,
    'seed': 42,
    'local_rank': -1,
    'tokenizer': 'iupac',
    'num_workers': 8,
    'debug': False,
    'log_level': 20,
    'patience': -1,
    'resume_from_checkpoint': False
}

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
