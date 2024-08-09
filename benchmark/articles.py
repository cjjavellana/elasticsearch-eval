import argparse
import threading
import queue
import requests
import numbers
import time

import pyarrow.dataset as ds

from elasticsearch import Elasticsearch
from datasetdownloader import IndexedDatasetDownloader

parser = argparse.ArgumentParser(description='Take full-text search benchmark between elastic search & mariadb')
parser.add_argument('-t', '--target', 
                    choices=['elasticsearch', 'mariadb'],
                    required=True,
                    help='That target datastore.')
parser.add_argument('-n', '--num-files', dest='num_files', type=int, help='The number of files to download')
parser.add_argument('-c', '--ingest-thread-count', dest='ingest_thread_count', default=5, type=int, help='The number of threads to be used to write data to the destination datastore')
parser.add_argument('--elastic-url', dest='elastic_url', help='The url of the elastic search cluster. Comma delimited.')
parser.add_argument('--elastic-username', dest='elastic_username', default='elastic', help='The username of the elastic search cluster')
parser.add_argument('--elastic-password', dest='elastic_password', help='The password of the elastic search cluster')

class IngestStats:

    def __init__(self, num_records):
        self.num_records = num_records

class MariaDBSink:

    def __init__(self):
        pass

class ElasticSearchSink:

    def __init__(self, index, elastic_url, username = None, password = None):
        self.elastic_url = elastic_url
        self.username = username
        self.index = index
        self.elastic_client = Elasticsearch(self.elastic_url, basic_auth=(username, password))
        print(f'Client Info {self.elastic_client.info()}')

    def save(self, document):
        return self.elastic_client.index(index=self.index, document=document)

    def stats(self):
        document_count = self.elastic_client.count(index=self.index)
        return IngestStats(num_records=document_count['count'])

class WikipediaDatasetLoader:

    POISON_PILL = -1

    # 
    # @param sink - The persistent store to load data to
    # @param thread_count - The number of file readers to open
    # @param src_data_dir - The directory where the test data is located
    def __init__(self, sink, thread_count = 3, src_data_dir='./'):
        self.sink = sink
        self.src_data_dir = src_data_dir
        # the number of threads to be used to load the files
        self.thread_count = thread_count
        # queue used for loading multiple dataset files concurrently
        self.q = queue.Queue()

    def load(self):
        # Create consumer threads
        for x in range(self.thread_count):
            threading.Thread(target=self.__data_consumer, daemon=True).start()

        self.__produce_data()
        
        # Wait for tasks to complete
        self.q.join()

        return self.sink.stats()

    def __produce_data(self):
        # Open the dataset
        wikipedia_dataset = ds.dataset(self.src_data_dir, format="parquet")

        for table_chunk in wikipedia_dataset.to_batches(columns=["url", "title", "text"]):
            title = table_chunk.to_pandas()
            self.q.put(title)

        # After we have put all the wikipedia data into the queue
        # Put the poison pill to signal to the consumer thread to shutdown
        for x in range(self.thread_count):
            self.q.put(self.POISON_PILL)

    def __data_consumer(self):
        while True:
            item = self.q.get()

            if self.__should_quit(item):
                self.q.task_done()
                break

            self.__process_item(item)
            self.q.task_done()
        
        print(f'Terminating {threading.get_native_id()}')

    def __process_item(self, item):
       for idx in item.index:
           # Construct an elasticsearch document
           url = item['url'][idx]
           title = item['title'][idx]
           text = item['text'][idx]
           print(f"{threading.get_native_id()} => {url}")

           document = {
               "url": url,
               "title": title,
               "text": text
           }

           resp = self.sink.save(document)

    def __should_quit(self, item):
        return isinstance(item, numbers.Number) and item == self.POISON_PILL

class ElasticSearchBenchmark:

    def __init__(
            self, 
            elastic_url = 'http://localhost:9200',
            elastic_username = 'elastic',
            elastic_password = 'elastic',
            max_index = 3,
            ingest_thread_count = 3
        ):
        data_dir = './test_data_dir'
        self.dataset_downloader = IndexedDatasetDownloader(max_index = max_index, dest_data_dir=data_dir)
        self.dataset_loader = WikipediaDatasetLoader(
                sink = ElasticSearchSink(
                    elastic_url = elastic_url,
                    index='idx-articles',
                    username=elastic_username,
                    password=elastic_password,
                ),
                thread_count=ingest_thread_count,
                src_data_dir = data_dir
            )

    def take(self):
        download_start_time = time.time()
        self.dataset_downloader.download()
        download_end_time = time.time()

        ingest_start_time = time.time()
        load_stats = self.dataset_loader.load()
        ingest_end_time = time.time()

        print(f'Download Elapsed Time: {download_end_time - download_start_time} seconds')
        print(f'Loaded {load_stats.num_records} documents in {ingest_end_time - ingest_start_time} seconds')

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)

    if args.target == 'elasticsearch':
        benchmark = ElasticSearchBenchmark(
                max_index=args.num_files,
                ingest_thread_count=args.ingest_thread_count
        )
        benchmark.take()
    if args.target == 'mariadb':
        pass

