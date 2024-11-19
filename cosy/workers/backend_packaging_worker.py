import json
import os
from queue import Queue
from cosy.config import CONFIG
from cosy.workers import Worker
from cosy.logger import logger
import time

from cosy.workers.util.tempo import calculate_content_tempo


class BackendPackagingWorker(Worker):
    """
    Worker class for packaging the output of the AI tools into a JSON file
    compatible with the CoSy backend.
    """

    def __init__(self, id: str, queue: Queue, output_directory: str) -> None:
        """
        Initialize the BackendPackagingWorker object.

        :param id: The worker ID
        :param queue: The queue to get tasks from
        :param output_directory: The directory to write the output files to
        """

        super().__init__(id, None, queue)
        self.output_directory = output_directory

    def process(
        self,
        input_file: str,
    ) -> None:
        """
        Process an input file by packaging it into a JSON file compatible with
        the CoSy backend.

        :param input_file: The input file to process
        :return: None
        """

        input_file_tool_id = os.path.basename(os.path.dirname(input_file))
        input_file_tool_type = CONFIG["tools"][input_file_tool_id]["type"]

        logger.debug(
            f"BackendPackagingWorker {self.id} processing file {input_file}"
            f" with tool type {input_file_tool_type}"
        )

        feedback_id = os.path.basename(input_file).split("_")[0]
        record_timestamp = (
            os.path.basename(input_file).split("_")[1].split("-")[0]
        )
        channel_nr = os.path.basename(input_file).split("-")[1].split(".")[0]
        output = {
            "feedbackId": feedback_id,
            "recordTimestamp": int(record_timestamp),
            "channelNr": int(channel_nr),
        }

        input_json = {}

        with open(input_file, "r") as j:
            input_json = json.loads(j.read())

        if input_file_tool_type == "ai_forcedalignment":
            output["contentTranscript"] = []
            output["contentTempo"] = {
                "dataContinous": [],
                "dataGlobal": [],
            }
            try:
                for idx, x in enumerate(input_json["Sentences"]):
                    # print(f"idx: {idx}, x: {x}")
                    output["contentTranscript"].append(
                        {
                            "timeStart": input_json["Start Times"][idx],
                            "timeEnd": input_json["End Times"][idx],
                            "value": x,
                        }
                    )
                output["contentTempo"] = calculate_content_tempo(input_json)

            except Exception as e:
                logger.error(f"Error packaging AI transcript analysis: {e}")

            if len(output["contentTranscript"]) == 0:
                logger.warning(
                    f"BackendPackagingWorker {self.id} no "
                    f"transcript data found in {input_file}"
                )
            elif len(output["contentTempo"]["dataContinous"]) == 0:
                logger.warning(
                    f"BackendPackagingWorker {self.id} no "
                    f"tempo data found in {input_file}"
                )

        if input_file_tool_type == "ai_nlp":
            output["contentNLP"] = {}
            try:
                output["contentNLP"]["keywords"] = input_json[
                    "Keyword Position List"
                ]
                output["contentNLP"]["questions"] = input_json["Question List"]
                output["contentNLP"]["nounCounts"] = input_json["Noun Counts"]
                output["contentNLP"]["verbCounts"] = input_json["Verb Counts"]
                output["contentNLP"]["adjCounts"] = input_json["ADJ Counts"]
                output["contentNLP"]["nounFrequencies"] = input_json[
                    "Noun Frequncies"
                ]
                output["contentNLP"]["verbFrequencies"] = input_json[
                    "Verb Frequencies"
                ]
                output["contentNLP"]["adjFrequencies"] = input_json[
                    "Adj Frequencies"
                ]
            except Exception as e:
                logger.error(f"Error packaging AI NLP analysis: {e}")

            if output["contentNLP"] == {}:
                logger.warning(
                    f"BackendPackagingWorker {self.id} no "
                    f"NLP data found in {input_file}"
                )

        elif input_file_tool_type == "ai_pitchloudness":
            output["contentPitch"] = {
                "dataContinous": [],
                "dataGlobal": [],
            }
            try:
                for idx, x in enumerate(input_json["Pitch Values"]):
                    output["contentPitch"]["dataContinous"].append(x)
                    output["contentPitch"]["dataGlobal"].append(
                        input_json["Pitch Statistics"][idx]
                    )
            except Exception as e:
                logger.error(f"Error packaging AI pitch anaylsis: {e}")
            if len(output["contentPitch"]["dataContinous"]) == 0:
                logger.warning(
                    f"BackendPackagingWorker {self.id} no "
                    f"pitch data found in {input_file}"
                )
            output["contentLoudness"] = {
                "dataContinous": [],
                "dataGlobal": [],
            }
            try:
                for idx, x in enumerate(input_json["Loudness Values"]):
                    output["contentLoudness"]["dataContinous"].append(x)
                    output["contentLoudness"]["dataGlobal"].append(
                        input_json["Loudness Statistics"][idx]
                    )
            except Exception as e:
                logger.error(f"Error packaging AI Loudness anaylsis: {e}")

        output_file_name = (
            os.path.basename(input_file).replace(".json", "")
            + "_"
            + str(int(time.time() * 1000))
            + ".json"
        )
        print(f"output_file_name: {output_file_name}")
        output_file_path = os.path.join(
            self.output_directory, output_file_name
        )

        with open(output_file_path, "w") as output_file:
            json.dump(output, output_file)
