import subprocess
import os
import sys
import threading
from queue import Queue
from cosy.workers import Worker
from cosy.logger import logger
from cosy.loading_status import increment_ready


class HotWorker(Worker):
    """
    Worker that runs a subprocess and communicates with it using pipes.
    """

    def __init__(
        self, id: str, launch_command: list[str], queue: Queue
    ) -> None:
        """
        Initialize the HotWorker object.

        :param id: The worker ID
        :param launch_command: The launch command to run the worker
        :param queue: The queue to get tasks from
        """
        super().__init__(id, launch_command, queue)
        self.busy = True
        self.start()

    def _create_pipes(self):
        """
        Create pipes for communication between the parent and child process.
        """

        self.pipe_read, self.pipe_write = os.pipe()
        self.pipe_read_file = os.fdopen(self.pipe_read, "r")

    def start(self):
        """
        Start the worker subprocess.
        """
        self._create_pipes()
        logger.debug(
            f"({self.id}) Starting HotWorker with launch command {self.base_command}"
        )
        command_with_fd = self.base_command + ["-f", str(self.pipe_write)]
        self.instance = subprocess.Popen(
            command_with_fd,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=sys.stderr,
            pass_fds=(self.pipe_write,),
            text=True,
        )
        os.close(self.pipe_write)  # Close the write end in the parent process.

        threading.Thread(target=self._instance_monitor, daemon=True).start()

    def _instance_monitor(self):
        """
        Monitor the worker subprocess and handle errors.
        """

        while True:
            try:
                message = self.pipe_read_file.readline().strip()
                if not message:
                    if self.instance.poll() is not None:
                        self.handle_error(returnCode=self.instance.returncode)
                        break
                    continue
            except Exception as e:
                logger.error(f"({self.id}) Error reading from pipe: {e}")
                self.handle_error(error=e)
                break

            if message == "ready":
                self.busy = False
                logger.debug(
                    f"({self.id}) Received 'ready' signal from the subprocess"
                )
                increment_ready()

    def handle_error(self, error=None, returnCode=None) -> None:
        """
        Handle errors in the worker subprocess.

        :param error: The error message
        :param returnCode: The return code of the subprocess
        """

        if error:
            logger.error(f"({self.id}) Error: {error}")
        if returnCode is not None:
            logger.error(f"({self.id}) Return code: {returnCode}")
        self.restart()

    def process(self, stdio_input: str) -> None:
        """
        Process a task by sending it to the worker subprocess.

        :param stdio_input: The input to send to the subprocess
        :return: None
        """

        if self.busy:
            logger.debug(f"({self.id}) Worker is busy")
            return False

        self.busy = True
        self.instance.stdin.write(f"{stdio_input}\n")
        self.instance.stdin.flush()
        self.busy = False

    def restart(self):
        """
        Restart the worker subprocess.
        """

        logger.debug(f"({self.id}) Restarting HotWorker")
        self.shutdown()
        self.start()

    def shutdown(self):
        """
        Shut down the worker subprocess.
        """

        logger.debug(f"({self.id}) Shutting down HotWorker")
        if self.instance.poll() is None:
            self.instance.terminate()
        self.pipe_read_file.close()
