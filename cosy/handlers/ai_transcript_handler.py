import threading
from cosy.config import CONFIG
from cosy.handlers import Handler
from cosy.logger import logger
import os

from cosy.workers import HotWorker


class AITranscriptHandler(Handler):
    """
    Handler class for the AI transcript tool.
    """

    def __init__(
        self,
        id: str,
        num_workers: int,
        worker_base_command: list[str],
    ) -> None:
        """
        Initialize the AITranscriptHandler object.

        :param id: The handler ID
        :param num_workers: The number of workers to create
        :param worker_base_command: The base command to run the workers
        """

        logger.debug(
            "Initializing AITranscriptHandler with base command "
            + str(worker_base_command)
        )
        super().__init__(id, num_workers, worker_base_command)
        self.init_workers()

    def init_workers(self) -> None:
        """
        Initialize the workers for the handler.

        :return: None
        """

        logger.debug(f"Initializing {self.num_workers} HotWorkers")
        for i in range(self.num_workers):
            logger.debug(f"Handler {self.id} initializing worker {i}")
            worker = HotWorker(
                f"{self.id}_worker_{i}", self.worker_base_command, self.queue
            )
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

        output_file = os.path.join(
            CONFIG["application_settings"]["data_dir"],
            self.id,
            os.path.basename(input_file).replace(".wav", ".json"),
        )
        self.queue.put_nowait(f"{input_file},{output_file}")

    def handle(self, input_file: str) -> None:
        """
        Handle a file by adding it to the queue.

        :param input_file: The file to process
        :return: None
        """

        self.add_job(input_file)
