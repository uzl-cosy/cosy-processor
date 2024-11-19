import threading
from cosy.config import CONFIG
from cosy.handlers import Handler
from cosy.logger import logger
import os

from cosy.workers import HotWorker


class AudioEnhancerHandler(Handler):
    """
    Handler class for the audio enhancer tool.
    """

    def __init__(
        self,
        id: str,
        num_workers: int,
        worker_base_command: list[str],
        plugin_file: str = None,
        state_file: str = None,
        # parameters: list,
    ) -> None:
        """
        Initialize the AudioEnhancerHandler object.

        :param id: The handler ID
        :param num_workers: The number of workers to create
        :param worker_base_command: The base command to run the workers
        :param plugin_file: The plugin file for the enhancer
        :param state_file: The state file for the audio plugin
        """

        logger.debug(
            "Initializing AudioEnhancerHandler with base command "
            + str(worker_base_command)
            + ' and plugin file "'
            + str(plugin_file)
            + '" and state file "'
            + str(state_file)
            + '"'
        )
        super().__init__(id, num_workers, worker_base_command)
        self.plugin_file = plugin_file
        self.state_file = state_file
        # self.parameters = parameters
        self.init_workers()

    def init_workers(self) -> None:
        """
        Initialize the workers for the handler.

        :return: None
        """

        logger.debug(f"Initializing {self.num_workers} HotWorkers")
        command = self.worker_base_command
        if self.plugin_file:
            command += ["-p", self.plugin_file]
        if self.state_file:
            command += ["-s", self.state_file]
        for i in range(self.num_workers):
            logger.debug(f"Handler {self.id} initializing worker {i}")
            worker = HotWorker(f"{self.id}_worker_{i}", command, self.queue)
            thread = threading.Thread(target=worker.wait_for_task, daemon=True)
            thread.start()
            self.workers.append(worker)
            self.worker_threads.append(thread)

    def add_job(self, input_file):
        output_file = os.path.join(
            CONFIG["application_settings"]["data_dir"],
            self.id,
            os.path.basename(input_file),
        )
        self.queue.put_nowait(f"{input_file},{output_file}")

    def handle(self, input_file: str) -> None:
        """
        Handle a file by adding it to the queue.

        :param input_file: The file to process
        :return: None
        """

        self.add_job(input_file)
