from abc import ABC, abstractmethod
from queue import Queue
import time

from cosy.logger import logger


class Worker(ABC):
    """
    Abstract class for a worker.
    This class governs a specific software process for audio processing.
    """

    def __init__(
        self,
        id: str,
        base_command: list[str],
        queue: Queue,
    ) -> None:
        """
        Initialize the Worker object.

        :param id: The worker ID
        :param base_command: The base command to run the worker
        :param queue: The queue to get tasks from
        """

        self.id = id
        self.base_command = base_command
        self.queue = queue
        self.busy = False

    def is_busy(self) -> bool:
        """
        Check if the worker is busy.

        :return: True if the worker is busy, False otherwise
        """
        return self.busy

    def wait_for_task(self):
        """
        Wait for a task to be added to the queue.

        :return: None
        """
        logger.debug(f"({self.id}) Worker waiting for task")
        while True:
            task = self.queue.get(block=True)

            # Wait until the worker is not busy
            while self.is_busy():
                logger.debug(f"({self.id}) Worker is busy, waiting...")
                time.sleep(1)  # Wait a bit before checking again

            logger.debug(f"({self.id}) Worker received task")
            self.process(task)
            self.queue.task_done()

    @classmethod
    @abstractmethod
    def process(self, *args, **kwargs) -> None:
        """
        Abstract method to process a task.

        :param args: Arguments for the task
        :param kwargs: Keyword arguments for the task
        :return: None
        """

        pass
