import os
import pyaudio
import wave
import numpy as np
import random
import string
import time
import multiprocessing
from cosy.logger import logger
from cosy.config import CONFIG
from cosy.stream_manager import (
    subscribe_stream,
    unsubscribe_stream,
    read_stream,
)


class Recorder:
    """
    Class to handle audio recording from a PyAudio stream.

    Attributes:
        format (int): Audio format
        channel_count (int): Number of audio channels
        channel_numbers (list): List of all channel numbers
        channel_numbers_selected (list): List of selected channel numbers
        rate (int): Sampling rate
        audio_device (str): Audio device name
        buffer_size (int): Number of frames per buffer
        chunk_length (int): Length of each audio chunk in seconds
        output_directory (str): Directory to save the audio chunks
        stop_event (multiprocessing.Event): Event to stop the recording process
        recording (bool): Flag to indicate if a recording is currently active
    """

    recorder_settings = CONFIG["tools"]["recorder"]["settings"]
    format = pyaudio.paInt16  # Audio format
    channel_count = (
        recorder_settings["channels"]
        if isinstance(recorder_settings["channels"], int)
        else max(recorder_settings["channels"])
    )
    channel_numbers = (
        [*range(1, channel_count + 1)]
        if isinstance(recorder_settings["channels"], int)
        else [*range(1, max(recorder_settings["channels"]) + 1)]
    )
    channel_numbers_selected = (
        [*range(1, recorder_settings["channels"] + 1)]
        if isinstance(recorder_settings["channels"], int)
        else recorder_settings["channels"]
    )
    rate = recorder_settings["sample_rate"]  # Sampling rate
    audio_device = recorder_settings["audio_device"]  # Audio device name
    buffer_size = 1024  # Number of frames per buffer
    chunk_length = recorder_settings[
        "chunk_length"
    ]  # Length of each audio chunk in seconds
    output_directory = CONFIG["application_settings"]["data_dir"] + "/recorder"

    def __init__(self) -> None:
        """Initiate a recorder object"""
        self.stop_event = multiprocessing.Event()
        self.recording = False

    def is_recording(self) -> bool:
        """Check if a recording is currently active"""
        return self.recording

    def generate_random_id() -> string:
        """Generate a random ID for the audio chunk."""
        return "".join(random.choices(string.ascii_uppercase, k=10))

    def save_channel(
        self,
        channel_data: list,
        channel_number: int,
        chunk_id: string,
        p: pyaudio.PyAudio,
    ) -> None:
        """Save a single channel's data to a WAV file."""
        file_name = os.path.join(
            self.output_directory, f"{chunk_id}-{channel_number}.wav"
        )
        wf = wave.open(file_name, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b"".join(channel_data))
        wf.close()

    def record(self, feedbackId: string) -> None:
        """Main function to handle audio recording and saving."""
        # Initialize PyAudio
        p = pyaudio.PyAudio()

        # Get the audio device index based on the name
        device_index = None
        for i in range(p.get_device_count()):
            if p.get_device_info_by_index(i)["name"] == self.audio_device:
                device_index = i
                break

        if device_index is None:
            logger.error(f"Audio device '{self.audio_device}' not found.")
            return

        stream = subscribe_stream()

        logger.info(
            f"Recorder started recording {self.channel_count}"
            f" audio channels from {self.audio_device}."
        )

        self.recording = True
        self.stop_event.clear()

        iteration = 0

        try:
            while not self.stop_event.is_set():
                logger.debug(f"Recording iteration {iteration}.")
                iteration += 1

                frames = []

                # Generate a new chunk ID for each recording
                # chunk_id = generate_random_id()
                chunk_id = feedbackId + "_" + str(int(time.time()))

                # Record audio
                for _ in range(
                    0, int(self.rate / self.buffer_size * self.chunk_length)
                ):
                    data = read_stream(self.buffer_size)
                    frames.append(data)
                    if self.stop_event.is_set():
                        break

                # Split channels and save
                for channel_idx, channel in enumerate(
                    self.channel_numbers_selected
                ):
                    channel_frames = []
                    for frame in frames:
                        frame_data = np.frombuffer(frame, dtype=np.int16)
                        channel_data = frame_data[
                            channel - 1 :: self.channel_count
                        ]
                        channel_frames.append(channel_data.tobytes())
                    self.save_channel(
                        channel_frames, channel_idx + 1, chunk_id, p
                    )

                logger.info(f"Chunk {chunk_id} saved.")

        except KeyboardInterrupt:
            logger.info("Recording stopped by user.")
        except Exception as e:
            logger.error(f"Error during recording: {e}")

        finally:
            unsubscribe_stream()
            # Stop and close the stream
            # stream.stop_stream()
            # stream.close()
            # p.terminate()

    def stop(self) -> bool:
        """Stop the active recording, if recording is active"""
        if self.stop_event.is_set():
            print("No recording running")
            return False
        self.stop_event.set()
        logger.info("Recording stopped.")
        self.recording = False
        return True
