University of Turku in the CAMDA 2014 Challenge
===============================================

This code implements the experiments of the University of Turku IT Department for the [CAMDA 2014 Challenge](http://camda2014.bioinf.jku.at). The program concerns analysis of the ICGC cancer dataset using various machine learning methods.

Challenge Dataset 1: ICGC Cancer Genomes
----------------------------------------

The [CAMDA site](http://camda2014.bioinf.jku.at/doku.php/contest_dataset) states that:

>From the comprehensive description of genomic, transcriptomic and epigenomic changes provided by ICGC, the main goal of this challenge is to gain novel biological insights to less well studied cancers selected here. However, we are not merely looking for 'old paradigm' cancer subtype classification!

>For this challenge, only processed data are provided. These cancers all have matched gene expression, microRNA expression, protein expression profiles, somatic CNV, and methylation.


The goal of the CAMDA 2014 challenge 1 (ICGC Cancer Genomes) is to use the ICGC cancer data to try to answer the questions:

1. **What are disease causal changes?** Can the integration of comprehensive multi-track -omics data give a clear answer?
2. **Can personalized medicine and rational drug treatment plans be derived from the data?** And how can we validate them down the road?

The ICGC datasets for the CAMDA challenge (all from the TCGA project):

* HNSC-US (Head and Neck Squamous Cell Carcinoma)
* LUAD-US (Lung Adenocarcinoma)
* KIRC-US (Kidney Renal Clear Cell Carcinoma)

Using the code
----------------------------------------
1. Install [Scikit-learn](http://scikit-learn.org/). At least version 14.1 is needed for the program to work. Versions after 14.1 have not been tested.
2. Run `python setup.py` and wait for the program to download the ICGC and NCI data and construct the relevant databases. This will take a few hours on a normal desktop machine. Make sure you have enough disk space (~35 Gb) for the resulting databases.
3. Run `python run.py` to produce the experimental results reported in the extended abstract. This will take a long time and a cluster environment with the [SLURM job scheduler](https://computing.llnl.gov/linux/slurm/) is recommended. To enable use of SLURM, run the program with the `--slurm` option.

Running individual experiments
------------------------------
After the databases are constructed using setup.py, individual experiments can be performed using the programs data/buildExamples.py and learn/learn.py.

1. Generate examples using src/data/buildExamples.py, using a defined experiment. The program will generate NumPy text format feature and label files and a metadata file containing further information on the examples, class and feature ids etc. For the currently implemented cancer remission experiment, run the following code `python buildExamples.py -x FEATURE_FILE -y LABEL_FILE -m METADATA_FILE -b DATABASE_FILE -e REMISSION -o "project=KIRC-US"`
2. Alternatively, run directly a machine learning experiment using src/learn/learn.py. Example generation is cached, so output files do not need to be defined. For the currently implemented cancer remission experiment, run the following code `python learn.py -e REMISSION -o "project=KIRC-US" -c svm.LinearSVC -a "C=logrange(-10,10)" -n 5`


###Generating examples for machine learning

Examples are generated by running an experiment. This can be done either explicitly by using data/buildExamples.py or automatically as part of machine learning when using learn/learn.py. In both cases, a set of command line options defines how the examples are generated. These options are:

1. -e = experiment template. The template is the name of a dictionary defined in settings.py, such as REMISSION. It defines how a set of examples is generated from the database, how they are selected, labeled and what features they use.
2. -o = template options. This command line option is a comma-separated list of key=value pairs, e.g. `key1=value1,key2=value2` and so on. Each key/value pair replaces the corresponding key/value pair in the experiment template. Each value is evaluated as Python-code, in the context of settings.py (i.e. all variables defined in settings.py can be used when defining a value). If the value cannot be evaluated, it is treated as a string.
3. -b = database. A path to the SQLite database. If the database is installed in the default location (DB_PATH in settings.py), the -b option can be omitted.
4. --hidden. By default all examples from the hidden set of donor ids are skipped (value "skip"). The other options allow inclusion of the hidden set in the examples, or generation of examples only from the hidden set.
5. -w = writer. The writer function can be either writeSVMLight or writeNumpyText (default), and defines the format of the output files.

###Performing a machine learning experiment

When using learn.py, the examples can be saved to the cache, from where they are automatically re-used as long as the database and experiment template remain unchanged. Caching is used automatically with learn.py. When using buildExamples.py, the output files must be defined. Example generation produces three output files.

1. -x = feature vectors, in the format defined by the writer function. By default, these are NumPy text vectors.
2. -y = example labels, one for each feature vector, in the format defined by the writer function. By default, these are NumPy text vectors. When using "writeSVMLight" as the writer, the labels are stored with the feature vectors in the -x file, and -y is not used.
3. -m = metadata. The metadata stores example metadata, including the experiment template and the class and feature names. When using the cache, the metadata is used to determine whether examples need to be regenerated.

###Using the cache without learn.py

For other machine learning implementations, the cache can be utilized by using the function getExperiments from the module data/cache.py. The function is documented, and will return the names of the three output files generated for a given experiment. If the output files already exist and both the database and the experiment template remain unchanged, the files are not regenerated.

### Running the programs

To generate examples using buildExamples.py, one could use e.g. the following command: `python buildExamples.py -x FEATURE_FILE -y LABEL_FILE -m METADATA_FILE -e REMISSION -o "project=KIRC-US"`. Here the REMISSION experiment template defines how examples are generated. The "project" option overrides the corresponding key in the REMISSION template, running the experiment for the KIRC-US dataset instead of the default one.

To run a machine learning experiment on the above experiment, using learn.py, one could use the following command `python learn.py -e REMISSION -o "project=KIRC-US" -c svm.LinearSVC -a "C=logrange(-10,10)" -n 5 -p 8`. Here the REMISSION experiment is run for the KIRC-US dataset, but as the cache is used, output files can be omitted. The classifier (-c) is imported from sklearn, and cross-validated with the arguments defined by option -a. Finally, -n 5 is used to define a 5-fold cross-validation and -p 8 the use of 8 parallel jobs when running the cross-validation.

### Experiments

* REMISSION: classification of cancer specimens into classes 1 (remission, decrease in or disappearance of signs and symptoms of cancer) or -1 (disease progress followed by death).
* CANCER_OR_CONTROL: classification of specimens into classes 1 (primary tumour) or -1 (primary normal control)
