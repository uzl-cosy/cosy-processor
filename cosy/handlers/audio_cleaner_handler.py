import threading
from cosy.config import CONFIG
from cosy.handlers import Handler
from cosy.logger import logger
import os
from collections import defaultdict
from cosy.workers import ColdWorker


class AudioCleanerHandler(Handler):
    """
    Handler class for the audio cleaner tool.
    """

    def __init__(
        self,
        id: str,
        num_workers: int,
        launch_command: list[str],
        compressor_plugin_file: str,
        compressor_state_file: str,
        # compressor_parameters: dict,
        gate_plugin_file: str,
        gate_state_file: str,
        # gate_parameters: dict,
    ) -> None:
        """
        Initialize the AudioCleanerHandler object.

        :param id: The handler ID
        :param num_workers: The number of workers to create
        :param launch_command: The base command to run the workers
        :param compressor_plugin_file: The plugin file for the compressor
        :param compressor_state_file: The state file for the compressor plugin
        :param gate_plugin_file: The plugin file for the gate
        :param gate_state_file: The state file for the gate plugin
        """

        logger.debug(f'Creating AudioCleanerHandler with ID "{id}"')
        self.waiting_list = defaultdict(list)
        worker_base_command = launch_command + [
            "-c",
            compressor_plugin_file,
            "-s",
            compressor_state_file,
            "-g",
            gate_plugin_file,
            "-t",
            gate_state_file,
            "-f",
            str(CONFIG["tools"]["recorder"]["settings"]["sample_rate"])
        ]
        super().__init__(id, num_workers, worker_base_command)
        self.init_workers()

    def init_workers(self) -> None:
        """
        Initialize the workers for the handler.

        :return: None
        """

        logger.debug(f"Initializing {self.num_workers} ColdWorkers")
        for i in range(self.num_workers):
            logger.debug(f"Handler {self.id} initializing worker {i}")
            worker = ColdWorker(
                f"{self.id}_worker_{i}", self.worker_base_command, self.queue
            )
            thread = threading.Thread(target=worker.wait_for_task, daemon=True)
            thread.start()
            self.workers.append(worker)
            self.worker_threads.append(thread)

    def add_job(self, input_file, sidechain_file):
        """
        Add a job to the queue.

        :param input_file: The file to process
        :return: None
        """

        output_file = os.path.join(
            CONFIG["application_settings"]["data_dir"],
            self.id,
            os.path.basename(input_file),
        )
        self.queue.put_nowait(
            ["-i", input_file, "-j", sidechain_file, "-o", output_file]
        )

    def handle(self, input_file: str) -> None:
        """
        Handle a file by adding it to a waiting list.
        When the second file of the chunk is received,
        the job is added to the queue.

        :param input_file: The file to process
        :return: None
        """

        chunk_id = os.path.basename(input_file).split("-")[0]
        if input_file not in self.waiting_list[chunk_id]:
            self.waiting_list[chunk_id].append(input_file)
        if len(self.waiting_list[chunk_id]) == 2:
            file_1 = self.waiting_list[chunk_id][0]
            file_2 = self.waiting_list[chunk_id][1]
            self.add_job(file_1, file_2)
            self.add_job(file_2, file_1)
            self.waiting_list.pop(chunk_id)
        else:
            logger.debug(
                f"Handler {self.id} waiting for"
                f" second file of chunk {chunk_id}"
            )
