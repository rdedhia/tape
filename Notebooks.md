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

Then you can run the notebooks in order

1. `1_generate_deeploc_data.ipynb`: Download the DeepLoc dataset from the internet in `fasta` format, and create
train, validation, and test splits, with any records above a specified max sequence length removed.

2. `2_fasta_to_lmdb.ipynb`: Create lightning memory-mapped databases (`lmdb`) from the train, validation, and test
split `fasta` files. This helps load the data faster when training the subcellular location model with TAPE.

3. [Google Colab](https://colab.research.google.com/drive/1RI6EPnU9c72DEMFdS0gI191MNghAe4P9#scrollTo=VaewL9hMSCnU)
notebook focused on embedding protein sequences using one of the TAPE pretrained models. This notebook could run on
a local machine, but benefits from the GPU resources available on Google Colab, because the process of embedding
the sequences is very compute intensive. In addition to containing code to embed the train, validation, and test
sequences for subcellular location, the notebook shows how to train downstream models (subcellular location in this
case) using the TAPE command line interface (`cli`). This notebook cannot be run without first running notebooks 1 and
2, and embedding the train/valid/test subcellular location files with this notebook is a prerequisite for running 
notebooks 5 and 6. **Note**: To run this notebook you will have to manually upload the `fasta` files in the `data` 
directory to Google Colab, because they are too large for git. You will also have to download the embedded `npz` files
from colab after embedding, and place them in the `data` folder of your local project. 

4. `4_visualize_subcellular_location.ipynb`: Use the pretrained embeddings from running the Google Colab notebook to 
visualize the top 2 or 3 principal components of the DeepLoc dataset compared to the classification labels.

5. `5_simple_model_analysis.ipynb`: Use the pretrained embeddings as features to prediction subcellular location,
using simple sklearn models instead of the deep learning NLP models from the TAPE project. This notebook also includes
some ROC curves to show the amount of signal for the different classes of the classifier.

6. `6_multitask.ipynb`: This notebook continues on the work from notebook 5 by focusing on the binary classification
(q2) membrane bound vs water soluble protein task from the DeepLoc dataset in addition to the q10 subcellular location
classification problem. As was done in the DeepLoc paper, we also attempted to treat this as a multitask  learning 
problem, which was not as successful as running the models in isolation.
