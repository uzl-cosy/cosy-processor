import os
import threading
from cosy.config import CONFIG
from cosy.handlers import Handler
from cosy.logger import logger

from cosy.workers import BackendPackagingWorker


class BackendPackagingHandler(Handler):
    """
    Handler class for packaging the output of the AI tools into a JSON file
    compatible with the CoSy backend.
    """

    def __init__(self, id: str, num_workers: int) -> None:
        """
        Initialize the BackendPackagingHandler object.

        :param id: The handler ID
        :param num_workers: The number of workers to create
        """

        logger.debug("Initializing BackendPackagingHandler")
        super().__init__(id, num_workers, [])
        self.init_workers()

    def init_workers(self) -> None:
        """
        Initialize the workers for the handler.

        :return: None
        """

        logger.debug(
            f"Initializing {self.num_workers} BackendPackagingHandler"
        )
        for i in range(self.num_workers):
            logger.debug(f"Handler {self.id} initializing worker {i}")
            worker = BackendPackagingWorker(
                f"{self.id}_worker_{i}",
                self.queue,
                os.path.join(
                    CONFIG["application_settings"]["data_dir"], self.id
                ),
            )
            thread = threading.Thread(target=worker.wait_for_task, daemon=True)
            thread.start()
            self.workers.append(worker)
            self.worker_threads.append(thread)

    def add_job(self, input_file: str):
        """
        Add a job to the queue.

        :param input_file: The file to process
        :return: None
        """

        self.queue.put_nowait(input_file)

    def handle(self, input_file: str) -> None:
        """
        Handle a file by adding it to the queue.

        :param input_file: The file to process
        :return: None
        """

        logger.debug(
            f"BackendPackagingHandler {self.id} handling {input_file}"
        )
        self.add_job(input_file)
