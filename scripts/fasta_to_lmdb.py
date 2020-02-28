from pathlib import Path
import pickle
import os
import sys

from Bio import SeqIO
import lmdb


PROJECT_DIR = Path(os.path.dirname(os.path.realpath(__file__))).parent

FASTA_TRAIN = list()
FASTA_VALID = list()
FASTA_TEST = list()


def read_fasta(fasta_path, fasta_list):
    train_file = PROJECT_DIR / fasta_path
    for sequence in SeqIO.parse(str(train_file), 'fasta'):
        id = sequence.id
        label = sequence.description.split()[1]
        seq = str(sequence.seq)
        fasta_list.append({
            'id': id,
            'label': label,
            'primary': seq
        })


def read_ss_lmdb():
    train_file = PROJECT_DIR / 'data/secondary_structure/secondary_structure_train.lmdb'
    env = lmdb.open(str(train_file), max_readers=1, readonly=True,
                    lock=False, readahead=False, meminit=False)

    with env.begin(write=False) as txn:
        num_examples = pickle.loads(txn.get(b'num_examples'))
        print(num_examples)

    index = 0
    with env.begin(write=False) as txn:
        item = pickle.loads(txn.get(str(index).encode()))
        if 'id' not in item:
            item['id'] = str(index)

    print(item)


def write_record_to_lmdb(db, key, value):
    """
    Write (key,value) to db
    """
    success = False
    while not success:
        txn = db.begin(write=True)
        try:
            txn.put(key, value)
            txn.commit()
            success = True
        except lmdb.MapFullError:
            txn.abort()
            # double the map_size
            curr_limit = db.info()['map_size']
            new_limit = curr_limit * 2
            print(f'Doubling LMDB map size to {new_limit}')
            db.set_mapsize(new_limit)


def write_sc_lmdb(split, fasta_list):
    map_size = sys.getsizeof(pickle.dumps(fasta_list)) * 10
    env = lmdb.open(str(PROJECT_DIR / f'data/deeploc/deeploc_{split}.lmdb'), map_size=map_size)
    for i in range(len(fasta_list)):
        write_record_to_lmdb(env, str(i).encode(), pickle.dumps(fasta_list[i]))
    write_record_to_lmdb(env, b'num_examples', pickle.dumps(len(fasta_list)))


def read_sc_lmdb(split, verbose_flag=False):
    env = lmdb.open(str(PROJECT_DIR / f'data/deeploc/deeploc_{split}.lmdb'))
    with env.begin(write=False) as txn:
        num_examples = pickle.loads(txn.get(b'num_examples'))
        print(f'{split} has num_examples={num_examples}')

    if verbose_flag:
        with env.begin(write=False) as txn:
            for index in range(num_examples):
                item = pickle.loads(txn.get(str(index).encode()))
                if 'id' not in item:
                    item['id'] = str(index)
                print(item)


def main():
    # Train
    read_fasta('data/train.fasta', FASTA_TRAIN)
    write_sc_lmdb('train', FASTA_TRAIN)
    read_sc_lmdb('train')

    # Validation
    read_fasta('data/valid.fasta', FASTA_VALID)
    write_sc_lmdb('valid', FASTA_VALID)
    read_sc_lmdb('valid')

    # Test
    read_fasta('data/test.fasta', FASTA_TEST)
    write_sc_lmdb('test', FASTA_TEST)
    read_sc_lmdb('test')


if __name__ == '__main__':
    main()
