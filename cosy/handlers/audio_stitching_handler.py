from collections import defaultdict
import os
import threading
from cosy.config import CONFIG
from cosy.handlers import Handler
from cosy.logger import logger

from cosy.workers import AudioStitchingWorker


class AudioStitchingHandler(Handler):
    """
    Handler class for stitching audio files together.
    """

    def __init__(self, id: str, num_workers: int) -> None:
        """
        Initialize the AudioStitchingHandler object.

        :param id: The handler ID
        :param num_workers: The number of workers to create
        """

        logger.debug("Initializing AudioStitchingHandler")
        super().__init__(id, num_workers, [])
        self.audio_files = defaultdict(list)
        self.init_workers()

    def init_workers(self) -> None:
        """
        Initialize the workers for the handler.

        :return: None
        """

        logger.debug(f"Initializing {self.num_workers} AudioStitchingHandler")
        for i in range(self.num_workers):
            logger.debug(f"Handler {self.id} initializing worker {i}")
            worker = AudioStitchingWorker(
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

    def add_job(self, input_files: list[str]):
        """
        Add a job to the queue.

        :param input_files: The files to process
        :return: None
        """

        logger.debug(f"AudioStitchingHandler {self.id} adding job")
        self.queue.put_nowait(input_files)

    def handle(self, input_file: str) -> None:
        """
        Handle a file by adding it to the queue.

        :param input_file: The file to process
        :return: None
        """

        logger.debug(f"AudioStitchingHandler {self.id} handling {input_file}")
        feedback_id = os.path.basename(input_file).split("_")[0]
        self.audio_files[feedback_id].append(input_file)
        self.add_job(self.audio_files[feedback_id])
