import os
from queue import Queue
import time
from cosy.workers import Worker
from cosy.logger import logger
from pydub import AudioSegment


class AudioStitchingWorker(Worker):
    """
    Worker class for stitching audio snippets together.
    """

    def __init__(self, id: str, queue: Queue, output_dir: str) -> None:
        """
        Initialize the AudioStitchingWorker object.

        :param id: The worker ID
        :param queue: The queue to get tasks from
        :param output_dir: The directory to write the stitched audio to
        """

        super().__init__(id, None, queue)
        self.output_dir = output_dir

    def stitch_audio(self, snippets):
        """
        Stitch audio snippets together.

        :param snippets: The audio snippets to stitch
        :return: The stitched audio
        """

        if not snippets:
            return None

        combined = None
        for snippet in snippets:
            try:
                sound = AudioSegment.from_file(snippet, format="wav")
                if combined is None:
                    combined = sound
                else:
                    combined += sound
            except Exception as e:
                logger.error(f"Error loading audio snippet {snippet}: {e}")
                continue

        return combined

    def process(self, input_files: list[str]) -> None:
        """
        Process a package by stitching audio snippets together.

        :param input_files: The audio snippets to stitch
        :return: None
        """

        logger.debug(
            f"AudioStitchingWorker {self.id} processing package {input_files}"
        )
        if not input_files:
            logger.error(
                f"AudioStitchingWorker {self.id} received empty package"
            )
            return

        try:
            feedbackId = os.path.basename(input_files[0]).split("_")[0]
        except IndexError as e:
            logger.error(f"Failed to extract feedback ID: {e}")
            return

        left_channel_snippets = [
            f for f in input_files if f.endswith("-1.wav")
        ]
        right_channel_snippets = [
            f for f in input_files if f.endswith("-2.wav")
        ]

        left_channel = self.stitch_audio(left_channel_snippets)
        right_channel = self.stitch_audio(right_channel_snippets)

        if left_channel is None or right_channel is None:
            logger.warn(
                f"AudioStitchingWorker {self.id} failed to"
                " stitch audio, one or more snippets are missing."
            )
            return

        if left_channel.duration_seconds != right_channel.duration_seconds:
            logger.warn(
                f"AudioStitchingWorker {self.id} failed to stitch"
                " audio, audio segments have different durations."
            )
            return

        try:
            stereo = AudioSegment.from_mono_audiosegments(
                left_channel, right_channel
            )
        except Exception as e:
            logger.error(f"Error creating stereo audio: {e}")
            return

        output_file = os.path.join(
            self.output_dir, f"{feedbackId}_{str(int(time.time()*1000))}.wav"
        )

        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except Exception as e:
                logger.error(
                    f"Error removing existing output file {output_file}: {e}"
                )
                return

        try:
            stereo.export(output_file, format="wav")
            logger.info(
                f"Successfully exported stitched audio to {output_file}"
            )
        except Exception as e:
            logger.error(f"Error exporting stitched audio: {e}")
