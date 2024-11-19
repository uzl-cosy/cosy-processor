from cosy.config import CONFIG
from pymitter import EventEmitter
from cosy.handlers import Handler
from cosy.logger import logger


def create_handlers() -> dict[str, Handler]:
    """
    Create handlers for each tool in the workflow.

    :return: A dictionary of handlers, where the key is the tool ID
    and the value is the handler object
    """

    needed_handlers = set()

    for tool_id, tool_props in CONFIG["workflow"].items():
        needed_handlers.add(tool_id)

    handlers = {}

    for tool_id, tool_props in CONFIG["tools"].items():
        # Only create handlers for tools that are needed
        if tool_id not in needed_handlers:
            continue

        if tool_props["type"] == "audio_enhancer":
            from cosy.handlers.audio_enhancer_handler import (
                AudioEnhancerHandler,
            )

            handler = AudioEnhancerHandler(
                tool_id,
                tool_props["num_workers"],
                CONFIG["tool_binaries"][tool_props["type"]]["base_command"],
                tool_props["settings"]["plugin_file"],
                tool_props["settings"].get("state_file", None),
            )

            handlers[tool_id] = handler
        elif tool_props["type"] == "audio_cleaner":
            from cosy.handlers.audio_cleaner_handler import (
                AudioCleanerHandler,
            )

            handler = AudioCleanerHandler(
                tool_id,
                tool_props["num_workers"],
                CONFIG["tool_binaries"][tool_props["type"]]["base_command"],
                tool_props["settings"]["compressor"]["plugin_file"],
                tool_props["settings"]["compressor"]["state_file"],
                tool_props["settings"]["gate"]["plugin_file"],
                tool_props["settings"]["gate"]["state_file"],
            )

            handlers[tool_id] = handler

        elif tool_props["type"] == "ai_transcript":
            from cosy.handlers.ai_transcript_handler import (
                AITranscriptHandler,
            )

            handler = AITranscriptHandler(
                tool_id,
                tool_props["num_workers"],
                CONFIG["tool_binaries"][tool_props["type"]]["base_command"],
            )

            handlers[tool_id] = handler

        elif tool_props["type"] == "ai_forcedalignment":
            from cosy.handlers.ai_forcedalignment_handler import (
                AIForcedAlignmentHandler,
            )

            handler = AIForcedAlignmentHandler(
                tool_id,
                tool_props["num_workers"],
                CONFIG["tool_binaries"][tool_props["type"]]["base_command"],
            )

            handlers[tool_id] = handler

        elif tool_props["type"] == "ai_forcedalignment_preprocessor":
            from cosy.handlers import (
                AIForcedAlignmentPreprocessingHandler,
            )

            handler = AIForcedAlignmentPreprocessingHandler(
                tool_id,
                tool_props["num_workers"],
                CONFIG["tool_binaries"][tool_props["type"]]["base_command"],
            )

            handlers[tool_id] = handler

        elif tool_props["type"] == "ai_forcedalignment_preprocessor_vad":
            from cosy.handlers import (
                AIForcedAlignmentPreprocessingVADHandler,
            )

            handler = AIForcedAlignmentPreprocessingVADHandler(
                tool_id,
                tool_props["num_workers"],
                CONFIG["tool_binaries"][tool_props["type"]]["base_command"],
            )

            handlers[tool_id] = handler

        elif tool_props["type"] == "ai_pitchloudness":
            from cosy.handlers.ai_pitchloudness_handler import (
                AIPitchLoudnessHandler,
            )

            handler = AIPitchLoudnessHandler(
                tool_id,
                tool_props["num_workers"],
                CONFIG["tool_binaries"][tool_props["type"]]["base_command"],
            )

            handlers[tool_id] = handler

        elif tool_props["type"] == "ai_nlp":
            from cosy.handlers.ai_nlp_handler import AINLPHandler

            handler = AINLPHandler(
                tool_id,
                tool_props["num_workers"],
                CONFIG["tool_binaries"][tool_props["type"]]["base_command"],
            )

            handlers[tool_id] = handler

        elif tool_props["type"] == "audio_stitcher":
            from cosy.handlers.audio_stitching_handler import (
                AudioStitchingHandler,
            )

            handler = AudioStitchingHandler(
                tool_id,
                tool_props["num_workers"],
            )

            handlers[tool_id] = handler

        elif tool_props["type"] == "backend_packager":
            from cosy.handlers.backend_packaging_handler import (
                BackendPackagingHandler,
            )

            handler = BackendPackagingHandler(
                tool_id,
                tool_props["num_workers"],
            )

            handlers[tool_id] = handler

        elif tool_props["type"] == "communicator":
            from cosy.handlers.communication_handler import (
                CommunicationHandler,
            )

            handler = CommunicationHandler(
                tool_id,
                tool_props["num_workers"],
                tool_props["settings"]["format"],
                tool_props["settings"]["url"],
                tool_props["settings"]["method"],
            )

            handlers[tool_id] = handler

    return handlers


def register_handlers(
    ee: EventEmitter,
    handlers: dict[str, Handler],
) -> None:
    """
    Register handlers for each tool in the workflow.

    :param ee: An instance of pymitter.EventEmitter to emit custom events.
    :param handlers: A dictionary of handlers, where the key is the tool ID
    and the value is the handler object
    :return: None
    """

    for tool_id, tool_props in CONFIG["workflow"].items():
        for input_tool_id in tool_props["input"]:
            if tool_id in handlers:
                logger.debug(
                    f'Registering handler "{tool_id}" for'
                    f' "file.created.{input_tool_id}"'
                )
                ee.on(
                    f"file.created.{input_tool_id}", handlers[tool_id].handle
                )
