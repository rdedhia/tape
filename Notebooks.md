# Notebooks

This repository includes a series of notebooks for working with the capabilities available in the `tape` project, with
a focus on the subcellular location dataset. The notebooks, with the exception of notebook 3 (hosted on Google colab),
are located in the `notebooks` directory, and are numbered to indicate the best order to run them in.

Prior to running any of the notebooks, set up your Python environment using `Python 3.6` and virtual environments.
Run these commands from the top level of the project.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-nbk.txt
```

Then you can run the notebooks. If you want to start from the raw DeepLoc dataset, you should run the notebooks in
order. However, this is not strictly necessary because we have prepopulated the `data` directory with most of the
intermediate and output data artifacts that are produced by the modeling notebook. Skip to the the `Data` section
for more details on each of the individual files.

1. `1_generate_deeploc_data.ipynb`: Download the DeepLoc dataset from the internet in `fasta` format, and create
train, validation, and test splits, with any records above a specified max sequence length removed. We run this 
notebook with two separate max sequence lengths: `6000` and `1024`. The upper limit of `6000` is to filter out
two sequences that otherwise cause memory issues when embedding the sequences with the `transformer` pretrained
model. The upper limit of `1024` should be applied if you plan to convert the `fasta` data to `lmdb` in notebook 2
and then use the sequences to train one of the downstream tasks using one of the deep learning models in TAPE.
This is because including larger sequences causes the GPU to run out of memory.

2. `2_fasta_to_lmdb.ipynb`: Create lightning memory-mapped databases (`lmdb`) from the train, validation, and test
split `fasta` files. This helps load the data faster when training the subcellular location model with TAPE. We
recommend running this notebook with a max sequence length of 1024.

3. [Google Colab](https://colab.research.google.com/drive/1RI6EPnU9c72DEMFdS0gI191MNghAe4P9#scrollTo=VaewL9hMSCnU)
notebook focused on embedding protein sequences using one of the TAPE pretrained models. This notebook could run on
a local machine, but benefits from the GPU resources available on Google Colab, because the process of embedding
the sequences is very compute intensive. In addition to containing code to embed the train, validation, and test
sequences for subcellular location, the notebook shows how to train downstream models (subcellular location in this
case) using the TAPE command line interface (`cli`). **Note**: To run this notebook you will have to manually upload 
the `fasta` files in the `data` directory to Google Colab, because they are too large for git. You will also have to 
download the embedded `npz` files from colab after embedding, and place them in the `data` folder of your local 
project. The embedding of all of the sequences may be too large to download from colab, in which case you can save
it to your Google Drive.

4. `4_visualize_subcellular_location.ipynb`: Use the pretrained embeddings from running the Google Colab notebook to 
visualize the top 2 or 3 principal components of the DeepLoc dataset compared to the classification labels.

5. `5_simple_model_analysis.ipynb`: Use the pretrained embeddings as features to prediction subcellular location,
using simple modeling techniques from the `scikit-learn` and `xgboost` libraries instead of the deep learning NLP 
models from the TAPE project. This notebook also includes some ROC curves to show how well the model is able to 
distinguish between different classes.

6. `6_multitask.ipynb`: This notebook continues on the work from notebook 5 by focusing on the binary classification
(q2) membrane bound vs water soluble protein task from the DeepLoc dataset in addition to the q10 subcellular location
classification problem. As was done in the DeepLoc paper, we also attempted to treat this as a multitask learning 
problem, which was not as successful as running the models in isolation.

## Data

`deeploc_data.fasta`: The raw dataset, downloaded from 
[DeepLoc](http://www.cbs.dtu.dk/services/DeepLoc-1.0/deeploc_data.fasta). This dataset contains 14404 protein
sequences. Each sequence has a unique protein ID and two classification labels. The first is for ten class
subcellular location, and the second is a binary classification problem between membrane bound and water soluble 
proteins. There are also some sequences for which the first label is `Cytoplasm-Nucleus` rather than one location of
the cell, or the second label is `Unknown`. Each of the sequences is also annotated as to whether it belongs in the
train or test set.

`deeploc_labels_q10.json` and `deeploc_labels_q2.json`: Labels for the q10 subcellular location and q2 membrane bound
vs water soluble classification tasks, respectively. Each of these files contains key/value pairs where the `key` is
a 6 digit sequence ID, and the value is the classification label.

`deeploc_data_6000.fasta` and `deeploc_data_1024.fasta`: Generated by notebook 1 by filtering out sequences with
a sequence length larger than `MAX_SEQ_LENGTH`, where `MAX_SEQ_LENGTH` is `6000` or `1024`. Any sequences with the
`Cytoplasm-Nucleus` label are also excluded from these files. We also include `deeploc_data_q2_6000.fasta`, which
excludes any sequences where the binary classification label is `Unknown`, and is used for PCA visualization.

`deeploc_train_6000.fasta`, `deeploc_valid_6000.fasta`, and `deeploc_test_6000.fasta`: In the first notebook, we split
the sequences in `deeploc_data_6000.fasta` into train, validation, and test splits. The train/test split is indicated
by the DeepLoc dataset, and we formulate the train/validation sets by taking a 90/10 split of the train set, stratified
by the subcellular location label.

`output_deeploc_6000.npz`: Embeddings stored as a `numpy` file with nested `numpy` and dictionary objects. These 
embeddings are produced by embedding the `deeploc_data_6000.fasta` file with the TAPE transformer model using the 
`tape-embed` or `tape-embed-distributed` command in Google Colab. These embeddings can then be used as features in 
other tasks. The embeddings are separated into explicit train/valid/test splits in `output_deeploc_train_6000.npz`, 
`output_deeploc_valid_6000.npz`, and `output_deeploc_test_6000.npz`.
