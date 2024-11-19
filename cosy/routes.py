from flask import Blueprint, Flask, request, make_response, jsonify
import psutil
import threading
import os

from cosy.logger import logger
from cosy.mic_status import check_microphone_status
from cosy.loading_status import loading_progress
from cosy.config import CONFIG
import json


def create_blueprint(ee, recorder):
    """
    Create a blueprint for the main routes of the application.

    :param ee: Event emitter
    :param recorder: Recorder object
    :return: Blueprint object
    """

    bp = Blueprint("main", __name__)

    @bp.route("/health", methods=["GET"])
    def health() -> Flask.response_class:
        """Return information about the computer system: CPU load and memory
        load"""
        return (
            jsonify(
                {
                    "cpuLoad": psutil.cpu_percent(),
                    "memoryLoad": psutil.virtual_memory().percent,
                }
            ),
            200,
        )

    @bp.route("/status", methods=["GET"])
    def status() -> Flask.response_class:
        """Return information about the media aspect of the system:
        Status of the microphones, loading and processing progress,
        as well as recording status
        """

        mic_status = check_microphone_status()

        # Processing progress status
        data_dir = CONFIG["application_settings"]["data_dir"]
        input_num = len(os.listdir(f"{data_dir}/recorder"))
        output_num = 0
        if os.path.exists(f"{data_dir}/backend_packager"):
            output_num = len(os.listdir(f"{data_dir}/backend_packager"))

        progress = 0.0
        if input_num > 0:
            percent = output_num / (input_num * 3)
            progress = float("{:.2f}".format(percent))

        loading = loading_progress()

        return (
            jsonify(
                {
                    "microphones": [
                        {"id": i, "active": mic_status[i]}
                        for i, _ in enumerate(mic_status)
                    ],
                    "loading": loading,
                    "progress": progress,
                    "recording": recorder.is_recording(),
                }
            ),
            200,
        )

    @bp.route("/recording/start", methods=["POST"])
    def recording_start() -> Flask.response_class:
        """Start a recording for the set number of channels
        (in config) into specified directory.
        Will do nothing if a recording is already running"""
        data = request.json
        print(data)
        if "feedbackId" not in data:
            return make_response(
                "Failed to start recording. Missing feedbackId", 400
            )

        keywords = {"Keywords": [], "Negative Words": []}
        # if "wordsToSay" not in data or "wordsNotToSay" not in data:
        #     return make_response(
        #         "Failed to start recording. Missing field", 400
        #     )

        if "wordsToSay" in data and "wordsNotToSay" in data:
            if not isinstance(data["wordsToSay"], list) or not isinstance(
                data["wordsNotToSay"], list
            ):
                return make_response(
                    "Failed to start recording. Keywords must be a list", 400
                )
            keywords["Keywords"] = data["wordsToSay"]
            keywords["Negative Words"] = data["wordsNotToSay"]

        keywords_path = "data/config/keywords/"
        feedback_id = data["feedbackId"]
        keywords_file_path = f"{keywords_path}/{feedback_id}.json"

        if not os.path.exists(keywords_path):
            os.makedirs(keywords_path)

        with open(keywords_file_path, "w") as f:
            json.dump(keywords, f)

        if recorder.is_recording():
            return make_response("Recording already startet", 400)
        threading.Thread(
            target=recorder.record, args=[data["feedbackId"]], daemon=True
        ).start()

        logger.debug('Emitting event "recording.start"')
        ee.emit("recording.start", data["feedbackId"])
        return make_response("Recording start", 200)

    @bp.route("/recording/stop", methods=["POST"])
    def recording_stop() -> Flask.response_class:
        """Stop the current recording, when a recording is running"""
        logger.debug('Emitting event "recording.stop"')
        ee.emit("recording.stop")
        if recorder.stop():
            return make_response("Recording stop", 200)
        return make_response("No recording running", 400)

    @bp.route("/debug/event/file_create", methods=["POST"])
    def debug_event_file_create() -> Flask.response_class:

        file_path = request.values["file_path"]

        if not file_path:
            return make_response("No file path", 400)

        logger.info(f"Debug file created event for: {file_path}")
        parent_dir = os.path.basename(os.path.dirname(file_path))
        logger.debug(f'Emitting event "file.created.{parent_dir}"')
        ee.emit(f"file.created.{parent_dir}", file_path)

        return make_response("Event triggered", 200)

    @bp.route("/debug/receiver/json", methods=["POST"])
    def debug_receiver_json() -> Flask.response_class:
        data = request.json
        logger.info(f"Debug receiver json: {data}")
        return jsonify("Receiver json received"), 200

    @bp.route("/debug/receiver/file", methods=["POST"])
    def debug_receiver_file() -> Flask.response_class:
        """Receive a file and return its size without storing the data"""
        file = request.files.get("file")
        if not file:
            return make_response("No file received", 400)
        file_size = len(file.read())
        return jsonify({"fileSize": file_size}), 200

    return bp
