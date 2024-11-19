from queue import Queue
import sys
from cosy.workers import Worker
from cosy.logger import logger
import subprocess


class ColdWorker(Worker):
    """
    Worker that runs a subprocess directly processing files given through the
    command line.
    """

    def __init__(self, id: str, base_command: list[str], queue: Queue) -> None:
        """
        Initialize the ColdWorker object.

        :param id: The worker ID
        :param base_command: The base command to run the worker
        :param queue: The queue to get tasks from
        """
        super().__init__(id, base_command, queue)

    def process(
        self,
        command_extension: list[str],
    ) -> None:
        """
        Process a command by running it with the worker.

        :param command_extension: The extension to the base command
        :return: None
        """
        command = self.base_command + command_extension
        logger.debug("ColdWorker processing with command " + str(command))
        subprocess.call(
            command,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
