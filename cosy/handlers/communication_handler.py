import threading
from cosy.handlers import Handler
from cosy.logger import logger

from cosy.workers import CommunicationWorker


class CommunicationHandler(Handler):

    def __init__(
        self, id: str, num_workers: int, format: str, url: str, method: str
    ) -> None:
        """
        Initialize the CommunicationHandler object.

        :param id: The handler ID
        :param num_workers: The number of workers to create
        :param format: The format of the data
        :param url: The URL to send the data to
        :param method: The HTTP method to use
        """

        logger.debug("Initializing CommunicationHandler")
        super().__init__(id, num_workers, [])
        self.init_workers()
        self.format = format
        self.url = url
        self.method = method

    def init_workers(self) -> None:
        """
        Initialize the workers for the handler.

        :return: None
        """

        logger.debug(f"Initializing {self.num_workers} CommunicationWorkers")
        for i in range(self.num_workers):
            logger.debug(f"Handler {self.id} initializing worker {i}")
            worker = CommunicationWorker(f"{self.id}_worker_{i}", self.queue)
            thread = threading.Thread(target=worker.wait_for_task, daemon=True)
            thread.start()
            self.workers.append(worker)
            self.worker_threads.append(thread)

    def add_job(self, input_file):
        """
        Add a job to the queue.

        :param input_file: The file to process
        :return: None
        """

        self.queue.put_nowait(
            {
                "url": self.url,
                "format": self.format,
                "method": self.method,
                "input_file": input_file,
            }
        )

    def handle(self, input_file: str) -> None:
        """
        Handle a file by adding it to the queue.

        :param input_file: The file to handle
        :return: None
        """

        logger.debug(f"CommunicationHandler {self.id} handling {input_file}")
        self.add_job(input_file)
