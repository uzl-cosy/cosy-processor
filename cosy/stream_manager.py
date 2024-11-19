import pyaudio

from cosy.config import CONFIG

recorder_settings = None
for tool in CONFIG["tools"]:
    if CONFIG["tools"][tool]["type"] == "audio_recorder":
        recorder_settings = CONFIG["tools"][tool]["settings"]
audio_device = recorder_settings["audio_device"]
RATE = recorder_settings["sample_rate"]
CHANNELS = recorder_settings["channels"]
FORMAT = pyaudio.paInt16
BUFFER_SIZE = 1024

stream = None
stream_listener = 0


def create_stream() -> pyaudio.Stream:
    """
    Create and return a PyAudio stream object.

    :return: PyAudio stream object
    """

    p = pyaudio.PyAudio()

    # Get the audio device index based on the name
    device_index = None
    for i in range(p.get_device_count()):
        if p.get_device_info_by_index(i)["name"] == audio_device:
            device_index = i
            break

    channel_count = (
        recorder_settings["channels"]
        if isinstance(recorder_settings["channels"], int)
        else max(recorder_settings["channels"])
    )

    stream = p.open(
        format=FORMAT,
        channels=channel_count,
        rate=RATE,
        input=True,
        frames_per_buffer=BUFFER_SIZE,
        input_device_index=device_index,
    )

    return stream


def read_stream(chunk_size):
    """
    Read a chunk of audio data from the PyAudio stream.

    :param chunk_size: Number of frames to read
    :return: Audio data chunk
    """

    global stream
    buffer = stream.read(chunk_size)

    return buffer


# def get_stream() -> pyaudio.Stream:
#     global stream
#     if stream is None:
#         stream = create_stream()
#     return stream


def subscribe_stream() -> None:
    """
    Subscribe to the PyAudio stream. If the stream does not exist, create it.

    :return: None
    """

    global stream, stream_listener
    if stream is None:
        stream = create_stream()
    stream_listener += 1


def unsubscribe_stream() -> None:
    """
    Unsubscribe from the PyAudio stream. If there are no listeners left, stop the stream.

    :return: None
    """

    global stream, stream_listener
    stream_listener -= 1
    if stream_listener < 1:
        stream.stop_stream()
        stream.close()
        stream = None
