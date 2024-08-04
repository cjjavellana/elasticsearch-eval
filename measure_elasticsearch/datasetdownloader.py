import threading
import queue
import requests
from pathlib import Path

class IndexedDatasetDownloader:

    def __init__(
            self, 
            thread_count = 5, 
            max_index = 5,
            zero_fill_index=True,
            zero_fill_count=5,
            file_format='parquet',
            dest_data_dir='./test_data_dir',
            url_format='https://huggingface.co/datasets/wikimedia/wikipedia/resolve/main/20231101.en/train-{index}-of-00041.parquet?download=true'):
        self.dataset_counter_lock = threading.Lock()
        self.dataset_counter = 0
        self.max_index = max_index
        self.zero_fill_index = zero_fill_index
        self.zero_fill_count = zero_fill_count
        self.url_format = url_format
        self.file_format = file_format
        self.thread_count = thread_count
        self.dest_data_dir = dest_data_dir
        self.worker_active = True
        self.q = queue.Queue()

    def load(self):
        # Create data dir (if not present)
        Path(self.dest_data_dir).mkdir(parents=True, exist_ok=True)

        for i in range(self.thread_count):
            threading.Thread(target=self.__load_worker, daemon=True).start()

        for x in range(self.max_index):
            self.q.put(x)

        self.q.join()
        self.worker_active = False

    def __load_worker(self):
        while self.worker_active:
            # Pop an item from the queue
            item = self.q.get()

            # Consult zero_fill_index to see whether we need to prefix our index
            # with zeroes
            index = str(item).zfill(self.zero_fill_count) if self.zero_fill_index == True else item

            # Construct the download url
            url = self.url_format.format(index=index)

            print(f'{threading.get_native_id()} Working on {url}')

            self.__download(url, '{dest_data_dir}/{index}.{file_format}'.format(
                dest_data_dir=self.dest_data_dir, index=index, file_format=self.file_format))
            self.q.task_done()

        print('Worker shutting down...')

    def __download(self, url, destination):
        try:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                with open(destination, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.exceptions.RequestException as e:
            print("Error downloading the file:", e)
