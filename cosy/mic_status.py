import pyaudio
import numpy as np
from cosy.logger import logger
from cosy.config import CONFIG
from cosy.stream_manager import (
    subscribe_stream,
    unsubscribe_stream,
    read_stream,
)

recorder_settings = None
for tool in CONFIG["tools"]:
    if CONFIG["tools"][tool]["type"] == "audio_recorder":
        recorder_settings = CONFIG["tools"][tool]["settings"]
audio_device = recorder_settings["audio_device"]
RATE = recorder_settings["sample_rate"]
CHANNELS = recorder_settings["channels"]
CHUNK = 1024
FORMAT = pyaudio.paInt16


def check_microphone_status() -> list:
    """
    Check the status of the microphones by listening to the audio input and
    checking if there is any input.

    :return: List of booleans indicating the status of the microphones
    """

    # channel_count = (
    #     recorder_settings["channels"]
    #     if isinstance(recorder_settings["channels"], int)
    #     else max(recorder_settings["channels"])
    # )
    # channel_numbers_selected = (
    #     [*range(1, recorder_settings["channels"] + 1)]
    #     if isinstance(recorder_settings["channels"], int)
    #     else recorder_settings["channels"]
    # )
    # channel_numbers_selected = [i - 1 for i in channel_numbers_selected]

    # stream = subscribe_stream()

    # data = read_stream(CHUNK)
    # audio_input = np.frombuffer(data, dtype=np.int16)

    # channel_data = np.row_stack(
    #     [audio_input[i::channel_count] for i in range(channel_count)]
    # )

    # # 10 as an arbitrary low threshold
    # has_input = [
    #     any(abs(sample) > 10 for sample in channel) for channel in channel_data
    # ]

    # unsubscribe_stream()

    # return has_input

    # TODO as of now, this is just a dummy return and needs to implemented / changed.
    # an idea would be to open one stream at startup in a parallel thread
    # and continuosly write the latest chunk into a variable.
    # This variable can be requested via the stream_manager.read_stream() function.
    # Changes would need to be made to the stream_manager file as well.

    return [True, True]


# print(check_microphone_status(2, 44100))
