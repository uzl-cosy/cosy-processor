import json
from queue import Queue
import requests
from cosy.workers import Worker
from cosy.logger import logger


class CommunicationWorker(Worker):
    def __init__(self, id: str, queue: Queue) -> None:
        super().__init__(id, None, queue)

    def process(
        self,
        package: dict[str, str],
    ) -> None:
        """
        Process a package by sending it to the receiver.

        :param package: The package to process
        :return: None
        """
        logger.debug(
            f"CommunicationWorker {self.id} processing package {package}"
        )
        if package["format"] == "json":
            headers = {"Content-Type": "application/json"}
            data = None
            with open(package["input_file"], "r") as f:
                data = f.read()
            try:
                response = None
                if package["method"] == "POST":
                    response = requests.post(
                        package["url"],
                        headers=headers,
                        data=data,
                        verify=False,
                    )
                elif package["method"] == "PUT":
                    response = requests.put(
                        package["url"],
                        headers=headers,
                        data=data,
                        verify=False,
                    )
                response_data = response.json()
                response_text = json.dumps(response_data)
                logger.debug(f"Response from receiver: {response_text}")
            except Exception as e:
                logger.error(f"Error sending data to receiver: {e}")
        elif package["format"] == "file":
            file = open(package["input_file"], "rb")
            try:
                response = None
                if package["method"] == "POST":
                    response = requests.post(
                        package["url"], files={"file": file}, verify=False
                    )
                response_data = response.json()
                response_text = json.dumps(response_data)
                logger.debug(f"Response from receiver: {response_text}")
            except Exception as e:
                logger.error(f"Error sending file to receiver: {e}")
            finally:
                file.close()
