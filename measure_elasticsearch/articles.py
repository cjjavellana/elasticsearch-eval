import argparse
import threading
import queue
import requests

from datasetdownloader import IndexedDatasetDownloader

parser = argparse.ArgumentParser(description='Take full-text search benchmark between elastic search & mariadb')
parser.add_argument('-t', '--target', 
                    choices=['elasticsearch', 'mariadb'],
                    required=True,
                    help='That target datastore.')
parser.add_argument('-m', '--maxindex', help='The maximum number of files to download')

class MariaDBSink:

    def __init__(self):
        pass

class ElasticSearchSink:

    def __init__(self):
        pass

    def save(data):
        pass

class WikipediaDatasetLoader:

    def __init__(self, data_dir='./'):
        self.data_dir = data_dir

class ElasticSearchBenchMark:

    def __init__(self, max_index = 3):
       self.dataset_loader = IndexedDatasetDownloader(max_index = max_index)

    def take(self):
        self.dataset_loader.load()

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)

    if args.target == 'elasticsearch':
        benchmark = ElasticSearchBenchMark()
        benchmark.take()
    if args.target == 'mariadb':
        pass
