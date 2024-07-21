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
This experiment relies on server infrastructures from AWS to run on. With that, ensure that you have an AWS account and that IAM users have been provisioned correctly.

## The Test Data

## Evaluation Criteria
This section describes the evaluation criteria with which Elastic Search & MariaDB is to be evaluated.

|S/No|Criteria|Elastic Search|MariaDB|Remarks|
|----|--------|--------------|-------|-------|
|1   |Full-text Search| | | |
|2   |Auto-completion| | | |

