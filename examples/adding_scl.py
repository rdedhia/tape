"""Example of how to add a task in tape.
In order to add a new task to TAPE, you must do a few things:
    1) Serialize the data into different splits (e.g. train, val, test) and place
       them in an appropriate folder inside the tape data directory.
    2) Define a dataset as a subclass of a torch Dataset. This should load and return
       the data from your splits.
    3) Define a collate_fn as a method of your dataset which will describe how
       to load in a batch of data (pytorch does not automatically batch variable
       length sequences).
    4) Register the task with TAPE
    5) Register models to the task
This file walks through how to create the 8-class secondary structure prediction
task using the pre-existing secondary structure data.
"""

from typing import Union, List, Tuple, Any, Dict
import torch
from torch.utils.data import Dataset
from pathlib import Path
import numpy as np

from tape.datasets import FastaDataset, pad_sequences
from tape.registry import registry
from tape.tokenizers import TAPETokenizer
from tape import ProteinBertForSequenceClassification
import logging
logger = logging.getLogger(__name__)


# Register the dataset as a new TAPE task. Since it's a classification task
# we need to tell TAPE how many labels the downstream model will use. If this
# wasn't a classification task, that argument could simply be dropped.
@registry.register_task('subcellular_location', num_labels=11)
class SubCellularLocationClassDataset(Dataset):
    """ Defines the subcellular location prediction dataset.
    Args:
        data_path (Union[str, Path]): Path to tape data directory. By default, this is
            assumed to be `./data`. Can be altered on the command line with the --data_dir
            flag.
        split (str): The specific dataset split to load often <train, valid, test>. In the
            case of secondary structure, there are three test datasets so each of these
            has a separate split flag.
        tokenizer (str): The model tokenizer to use when returning tokenized indices.
        in_memory (bool): Whether to load the entire dataset into memory or to keep
            it on disk.
    """

    def __init__(self,
                 data_path: Union[str, Path],
                 split: str,
                 tokenizer: Union[str, TAPETokenizer] = 'iupac',
                 in_memory: bool = False):

        if split not in ('train', 'test', 'valid'):
            raise ValueError(f"Unrecognized split: {split}. Must be one of "
                             f"['train', 'test', 'valid']")

        if isinstance(tokenizer, str):
            # If you get tokenizer in as a string, create an actual tokenizer
            tokenizer = TAPETokenizer(vocab=tokenizer)
        self.tokenizer = tokenizer

        # Define the path to the data file. There are three helper datasets
        # that you can import from tape.datasets - a FastaDataset,
        # a JSONDataset, and an LMDBDataset. You can use these to load raw
        # data from your files (or of course, you can do this manually).
        data_path = Path(data_path)
        data_file = f'deeploc_{split}.fasta'
        self.data = FastaDataset(data_path / data_file, in_memory=in_memory)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int):
        """ Return an item from the dataset. We've got an LMDBDataset that
            will load the raw data and return dictionaries. We have to then
            take that, load the keys that we need, tokenize and convert
            the amino acids to ids, and return the result.
        """
        item = self.data[index]
        # tokenize + convert to numpy
        token_ids = self.tokenizer.encode(item['primary'])
        # this will be the attention mask - we'll pad it out in
        # collate_fn
        input_mask = np.ones_like(token_ids)

        # pad with -1s because of cls/sep tokens
        label = int(item['label'].split(" ")[1])

        return token_ids, input_mask, label

    def collate_fn(self, batch: List[Tuple[Any, ...]]) -> Dict[str, torch.Tensor]:
        """ Define a collate_fn to convert the variable length sequences into
            a batch of torch tensors. token ids and mask should be padded with
            zeros. Labels for classification should be padded with -1.
            This takes in a list of outputs from the dataset's __getitem__
            method. You can use the `pad_sequences` helper function to pad
            a list of numpy arrays.
        """
        input_ids, input_mask, scl_label = tuple(zip(*batch))
        input_ids = torch.from_numpy(pad_sequences(input_ids, 0))
        input_mask = torch.from_numpy(pad_sequences(input_mask, 0))
        scl_label = torch.LongTensor(scl_label)

        output = {'input_ids': input_ids,
                  'input_mask': input_mask,
                  'targets': scl_label}

        return output


registry.register_task_model(
    'subcellular_location', 'transformer', ProteinBertForSequenceClassification)


if __name__ == '__main__':
    """ To actually run the task, you can do one of two things. You can
    simply import the appropriate run function from tape.main. The
    possible functions are `run_train`, `run_train_distributed`, and
    `run_eval`. Alternatively, you can add this dataset directly to
    tape/datasets.py.
    """
    TRAIN_ARGS = {
        'model_type': 'transformer',
        'task': 'subcellular_location',
        'learning_rate': 0.0001,
        'batch_size': 2,
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
        'data_dir': '../data',
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

    from tape.training import run_train
    run_train(**TRAIN_ARGS)
