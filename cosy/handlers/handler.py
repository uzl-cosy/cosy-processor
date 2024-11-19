from abc import ABC, abstractmethod
import queue


class Handler(ABC):
    """
    Abstract class for a handler. This class uses an internal queue
    to then distribute tasks to its workers.
    """

    def __init__(
        self, id: str, num_workers: int, worker_base_command: list[str]
    ) -> None:
        """
        Initialize the Handler object.

        :param id: The handler ID
        :param num_workers: The number of workers to create
        :param worker_base_command: The base command to run the workers
        """

        self.id = id
        self.num_workers = num_workers
        self.worker_base_command = worker_base_command
        self.workers = []
        self.worker_threads = []
        self.queue = queue.Queue()

    def get_id(self) -> str:
        """
        Get the handler ID.

        :return: The handler ID
        """

        return self.id

    @classmethod
    @abstractmethod
    def handle(self, input_file: str) -> None:
        """
        Abstract method to handle a file.

        :param input_file: The file to handle
        :return: None
        """

        pass
