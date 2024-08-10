# Performance evaluation of Elastic Search vs MariaDB

## Purpose
The goal of this experiment is to obtain empirical data with regards to the performance of Elastic Search and MariaDB in relation to the following tasks:

1. Full-text Search
2. Real-time Aggregation

## Replicating This Experiment

1. Create a local development environment

```bash
$ python3 -m venv .eseval
```

2. Install Dependencies

```
$ pip install ansible
$ pip install boto3
$ ansible-galaxy collection install --force amazon.aws
```

3. Setup AWS Account

This experiment relies on AWS. Ensure that you have an AWS account and that IAM users have been provisioned correctly.

A few hundred EC2 VMs were harmed in building this script.

## The Test Dataset

Test data is a [wikipedia](https://huggingface.co/datasets/wikimedia/wikipedia/viewer/20231101.en) dump from huggingface. The size of the dataset is approx 11GB.

## Running The Benchmark

1. Create a virtual environment for the benchmark

```bash
$ cd benchmark
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

2. Execute Benchmark

For taking elasticsearch benchmark
```bash
$ python articles.py -t elasticsearch --num-files 10 --ingest-thread-count 10
```

See help documentation to know more of start up parameters
```bash
$ python articles.py --help
```

For taking mariadb benchmark
```bash
```

## Evaluation Criteria
This section describes the evaluation criteria with which Elastic Search & MariaDB is to be evaluated.

|S/No|Criteria|Elastic Search|MariaDB|Remarks|
|----|--------|--------------|-------|-------|
|1   |Full-text Search| | | |
|2   |Auto-completion| | | |


