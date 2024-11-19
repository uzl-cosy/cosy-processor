from collections import defaultdict
import threading
from cosy.config import CONFIG
from cosy.handlers import Handler
from cosy.logger import logger
import os

from cosy.workers import ColdWorker


class AIForcedAlignmentPreprocessingHandler(Handler):
    """
    Handler class for the AI forced alignment preprocessing tool.
    """

    def __init__(
        self,
        id: str,
        num_workers: int,
        worker_base_command: list[str],
    ) -> None:
        """
        Initialize the AIForcedAlignmentPreprocessingHandler object.

        :param id: The handler ID
        :param num_workers: The number of workers to create
        :param worker_base_command: The base command to run the workers
        """

        logger.debug(
            "Initializing AIForcedAlignmentPreprocessingHandler with"
            " base command " + str(worker_base_command)
        )
        super().__init__(id, num_workers, worker_base_command)
        self.waiting_list = defaultdict(list)
        self.init_workers()

    def init_workers(self) -> None:
        """
        Initialize the workers for the handler.

        :return: None
        """

        logger.debug(f"Initializing {self.num_workers} HotWorkers")
        for i in range(self.num_workers):
            logger.debug(f"Handler {self.id} initializing worker {i}")
            worker = ColdWorker(
                f"{self.id}_worker_{i}", self.worker_base_command, self.queue
            )
            thread = threading.Thread(target=worker.wait_for_task, daemon=True)
            thread.start()
            self.workers.append(worker)
            self.worker_threads.append(thread)

    def add_job(
        self,
        input_audio_file_1,
        input_audio_file_2,
        output_audio_file_1,
        output_audio_file_2,
    ):
        """
        Add a job to the queue.

        :param input_audio_file_1: The first audio file (channel) to process
        :param input_audio_file_2: The second audio (channel) file to process
        :param output_audio_file_1: The first output audio (channel) file
        :param output_audio_file_2: The second output audio (channel) file
        :return: None
        """

        self.queue.put_nowait(
            [
                input_audio_file_1,
                input_audio_file_2,
                output_audio_file_1,
                output_audio_file_2,
            ]
        )

    def handle(self, input_file: str) -> None:
        """
        Handle an input file by adding it to the waiting list and
        creating a job when the second file of the chunk is received.

        :param input_file: The file to process
        :return: None
        """

        chunk_id = os.path.basename(input_file).split("-")[0]
        if input_file not in self.waiting_list[chunk_id]:
            self.waiting_list[chunk_id].append(input_file)
        if len(self.waiting_list[chunk_id]) == 2:
            input_file_1 = self.waiting_list[chunk_id][0]
            input_file_2 = self.waiting_list[chunk_id][1]
            output_file_1 = os.path.join(
                CONFIG["application_settings"]["data_dir"],
                self.id,
                os.path.basename(input_file_1),
            )
            output_file_2 = os.path.join(
                CONFIG["application_settings"]["data_dir"],
                self.id,
                os.path.basename(input_file_2),
            )
            self.add_job(
                input_file_1, input_file_2, output_file_1, output_file_2
            )
            self.waiting_list.pop(chunk_id)
        else:
            logger.debug(
                f"Handler {self.id} waiting for"
                f" second file of chunk {chunk_id}"
            )
