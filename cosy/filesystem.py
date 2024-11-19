from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from pymitter import EventEmitter
from cosy.config import CONFIG
from cosy.logger import logger

DATA_DIRECTORY = CONFIG["application_settings"]["data_dir"]


def create_filesystem_observer(ee: EventEmitter):
    """
    Create a filesystem observer that monitors a specific directory
    for file creation events. When a file with a '.wav' or '.json'
    extension is created, it logs the event and emits a custom
    event using the provided EventEmitter.

    Parameters:
    - ee (EventEmitter): An instance of pymitter.EventEmitter
    to emit custom events.

    Returns:
    - Observer: An instance of watchdog.observers.Observer configured
    to monitor the specified directory for file creation events.
    """

    class CustomFileSystemEventHandler(FileSystemEventHandler):
        def on_created(self, event) -> None:
            if event.is_directory:
                return
            if event.src_path.endswith(".wav") or event.src_path.endswith(
                ".json"
            ):
                logger.info(f"File created: {event.src_path}")
                parent_dir = os.path.basename(os.path.dirname(event.src_path))
                logger.debug(f'Emitting event "file.created.{parent_dir}"')
                ee.emit(f"file.created.{parent_dir}", event.src_path)

    file_system_event_handler = CustomFileSystemEventHandler()
    observer = Observer()
    observer.schedule(
        file_system_event_handler,
        CONFIG["application_settings"]["data_dir"],
        recursive=True,
    )
    return observer


def create_node_folders() -> None:
    """
    Create a folder for each tool in the workflow.
    """

    # create folder
    for tool_id, _ in CONFIG["workflow"].items():
        if not os.path.exists(DATA_DIRECTORY + "/" + tool_id):
            os.makedirs(os.path.abspath(DATA_DIRECTORY + "/" + tool_id))


def setup_data_dir():
    """
    Create the data directory if it does not exist and clean it up
    if the cleanup_on_launch setting is set to True.
    """

    if (
        os.path.exists(os.path.abspath(DATA_DIRECTORY))
        and CONFIG["application_settings"]["cleanup_on_launch"] is True
    ):
        logger.info(f"Cleaning up {DATA_DIRECTORY}")
        import shutil

        shutil.rmtree(os.path.abspath(DATA_DIRECTORY))
    if not os.path.exists(os.path.abspath(DATA_DIRECTORY)):
        os.makedirs(os.path.abspath(DATA_DIRECTORY))

    create_node_folders()
