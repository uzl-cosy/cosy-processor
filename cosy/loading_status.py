from cosy.config import CONFIG
from cosy.logger import logger

"""
Module to check the loading progress of the system.
"""

# Loading progress status
HOT_TYPES = [
    "audio_enhancer",
    "ai_forcedalignment",
    "ai_forcedalignment_preprocessor_vad",
    "ai_nlp",
    "ai_pitchloudness",
    "ai_transcript",
]

ready_count = 0

num_hot_worker = 0
loaded_tools = list(CONFIG["workflow"].keys())
for i in loaded_tools:
    if i in CONFIG["tools"] and CONFIG["tools"][i]["type"] in HOT_TYPES:
        num_hot_worker += CONFIG["tools"][i]["num_workers"]


def increment_ready() -> None:
    """
    Increment the number of ready hot workers.
    """

    global ready_count
    ready_count += 1


def loading_progress() -> float:
    """
    Return the loading progress of the system.
    """

    global ready_count, num_hot_worker
    progress = 0.0
    if num_hot_worker > 0:
        percent = ready_count / (num_hot_worker)
        progress = float("{:.2f}".format(percent))
    if num_hot_worker == 0:
        return 1.0
    return progress
