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
parser.add_argument('-m', '--max-index', dest='max_index', type=int, help='The maximum number of files to download')

class MariaDBSink:

    def __init__(self):
        pass

class ElasticSearchSink:

    def __init__(self):
        pass

    def save(data):
        pass

class WikipediaDatasetLoader:

    # 
    # @param sink - The persistent store to load data to
    # @param thread_count - The number of file readers to open
    # @param src_data_dir - The directory where the test data is located
    def __init__(self, sink, thread_count = 3, max_index = 5, src_data_dir='./'):
        self.sink = sink
        self.src_data_dir = src_data_dir
        self.max_index = max_index
        # the number of threads to be used to load the files
        self.thread_count = thread_count
        # queue used for loading multiple dataset files concurrently
        self.q = queue.Queue()
        self.is_worker_active = True

    def load(self):
        # Create background workers
        for x in range(self.thread_count):
            threading.Thread(target=self.__load_internal, daemon=True).start()

        # Put the task into the queue for processing
        for x in range(self.max_index):
            self.q.put(x)

        self.q.join() 

    def __load_internal(self):
        while self.is_worker_active:
            item = self.q.get()
            print(f'{threading.get_native_id()} Working on {item}')
            self.q.task_done()


class ElasticSearchBenchmark:

    def __init__(self, max_index = 3):
       self.dataset_downloader = IndexedDatasetDownloader(max_index = max_index)
       self.dataset_loader = WikipediaDatasetLoader(
               sink = ElasticSearchSink(), max_index = max_index, src_data_dir = './test_data_dir')

    def take(self):
        self.dataset_downloader.download()
        self.dataset_loader.load()

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)

    if args.target == 'elasticsearch':
        benchmark = ElasticSearchBenchmark(max_index=args.max_index)
        benchmark.take()
    if args.target == 'mariadb':
        pass
