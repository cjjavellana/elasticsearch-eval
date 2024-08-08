import argparse
import threading
import queue
import requests
import numbers

import pyarrow.dataset as ds

from datasetdownloader import IndexedDatasetDownloader

parser = argparse.ArgumentParser(description='Take full-text search benchmark between elastic search & mariadb')
parser.add_argument('-t', '--target', 
                    choices=['elasticsearch', 'mariadb'],
                    required=True,
                    help='That target datastore.')
parser.add_argument('-n', '--num-files', dest='num_files', type=int, help='The number of files to download')

class MariaDBSink:

    def __init__(self):
        pass

class ElasticSearchSink:

    def __init__(self):
        pass

    def save(data):
        pass

class WikipediaDatasetLoader:

    POISON_PILL = -1

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

    def load(self):
        # Create consumer threads
        for x in range(self.thread_count):
            threading.Thread(target=self.__data_consumer, daemon=True).start()

        self.__produce_data()
        
        # Wait for tasks to complete
        self.q.join()

    def __produce_data(self):
        # Open the dataset
        wikipedia_dataset = ds.dataset(self.src_data_dir, format="parquet")
        print(f'{wikipedia_dataset.files}')

        for table_chunk in wikipedia_dataset.to_batches(columns=["url", "title"]):
            title = table_chunk.to_pandas()
            self.q.put(title)

        # After we have put all the wikipedia data into the queue
        # Put the poison pill to signal to the consumer thread to shutdown
        for x in range(self.thread_count):
            self.q.put(self.POISON_PILL)

    def __data_consumer(self):
        while True:
            item = self.q.get()

            if isinstance(item, numbers.Number) and item == self.POISON_PILL:
                self.q.task_done()
                break
           
            # Item is a pandas DataFrame
            for idx in item.index:
                print(f"{threading.get_native_id()} => {item['url'][idx]} : {item['title'][idx]}")

            self.q.task_done()
        
        print(f'Terminating {threading.get_native_id()}')


class ElasticSearchBenchmark:

    def __init__(self, max_index = 3):
        data_dir = './test_data_dir'
        self.dataset_downloader = IndexedDatasetDownloader(max_index = max_index, dest_data_dir=data_dir)
        self.dataset_loader = WikipediaDatasetLoader(
                sink = ElasticSearchSink(), max_index = max_index, src_data_dir = data_dir)

    def take(self):
        self.dataset_downloader.download()
        self.dataset_loader.load()

if __name__ == '__main__':
    args = parser.parse_args()
    print(args)

    if args.target == 'elasticsearch':
        benchmark = ElasticSearchBenchmark(max_index=args.num_files)
        benchmark.take()
    if args.target == 'mariadb':
        pass
