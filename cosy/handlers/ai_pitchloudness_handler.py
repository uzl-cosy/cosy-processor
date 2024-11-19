from collections import defaultdict
import threading
from cosy.config import CONFIG
from cosy.handlers import Handler
from cosy.logger import logger
import os

from cosy.workers import HotWorker


class AIPitchLoudnessHandler(Handler):
    """
    Handler class for the AI pitch and loudness tool.
    """

    def __init__(
        self,
        id: str,
        num_workers: int,
        worker_base_command: list[str],
    ) -> None:
        """
        Initialize the AIPitchLoudnessHandler object.

        :param id: The handler ID
        :param num_workers: The number of workers to create
        :param worker_base_command: The base command to run the workers
        """

        logger.debug(
            "Initializing AIPitchLoudnessHandler with base command "
            + str(worker_base_command)
        )
        super().__init__(id, num_workers, worker_base_command)
        self.partial_jobs = defaultdict(lambda: {"json": None, "audio": None})
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

    def add_job(self, input_audio_file, input_json_file, output_json_file):
        """
        Add a job to the queue.

        :param input_audio_file: The audio file to process
        :param input_json_file: The json file to process
        :param output_json_file: The output json file
        :return: None
        """

        self.queue.put_nowait(
            f"{input_audio_file},{input_json_file},{output_json_file}"
        )

    def handle(self, input_file: str) -> None:
        """
        Handle an input file by adding first creating a partial job,
        then waiting for the matching json or audio file to create a full job.
        If a full job is created, add it to the queue.

        :param input_file: The file to process
        :return: None
        """

        chunk_id = os.path.basename(input_file).split(".")[0]
        if input_file.endswith(".json"):
            self.partial_jobs[chunk_id]["json"] = input_file
            logger.debug(f"Handler {self.id} received json file {input_file}")
        elif input_file.endswith(".wav"):
            self.partial_jobs[chunk_id]["audio"] = input_file
            logger.debug(f"Handler {self.id} received audio file {input_file}")

        if (
            self.partial_jobs[chunk_id]["json"]
            and self.partial_jobs[chunk_id]["audio"]
        ):
            output_json_file = os.path.join(
                CONFIG["application_settings"]["data_dir"],
                self.id,
                os.path.basename(self.partial_jobs[chunk_id]["json"]),
            )
            self.add_job(
                self.partial_jobs[chunk_id]["audio"],
                self.partial_jobs[chunk_id]["json"],
                output_json_file,
            )
            logger.debug(f"Handler {self.id} added job for chunk {chunk_id}")
            del self.partial_jobs[chunk_id]
