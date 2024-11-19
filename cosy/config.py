import argparse
import yaml

from cosy.logger import logger


parser = argparse.ArgumentParser(description="CoSy Device Application")
parser.add_argument(
    "-c",
    "--config",
    help="Path to the configuration file(s)",
    # default="config.yml",
    nargs="*",
)
parser.add_argument(
    "-m",
    "--mic",
    help="Name of microphone to use",
    default="",
    type=str,
)
args = parser.parse_args()


def merge_dicts(dict1, dict2, overwrite_keys=None):
    """
    Recursively merges two dictionaries. If a key's value is a dictionary in both dictionaries,
    the dictionaries are merged recursively. Otherwise, the value from dict2 is used.

    If overwrite_keys is provided, the values of these keys will be completely taken from dict2.
    """
    if dict2 is None:
        return dict1.copy()

    if overwrite_keys is None:
        overwrite_keys = set()

    result = dict1.copy()  # Make a copy of dict1 to avoid modifying it
    for key, value in dict2.items():
        if key in result:
            if key in overwrite_keys:
                result[key] = value
            elif isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value, overwrite_keys)
            else:
                result[key] = value
        else:
            result[key] = value
    return result


def load_config():
    """
    Load the configuration from the default configuration file and any additional
    configuration files passed as arguments. The additional configuration files
    will overwrite the default configuration values.

    :return: The loaded configuration
    """

    config = None

    # Load default configuration
    try:
        with open("config/default.yml", "r") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(
            "Default configuration file not found. Please make sure"
            " that the default.yml configuration file is present."
        )
        exit(1)

    # Load configuration from command line
    if args.config is None:
        args.config = []
    for config_file in args.config:
        try:
            with open(config_file, "r") as file:
                config = merge_dicts(
                    config, yaml.safe_load(file), overwrite_keys={"workflow"}
                )
        except FileNotFoundError:
            logger.error(f"Configuration file {config_file} not found.")
            exit(1)

    # Set microphone from arguments
    if args.mic != "":
        for tool in config["tools"]:
            if config["tools"][tool]["type"] == "audio_recorder":
                config["tools"][tool]["settings"]["audio_device"] = args.mic

    return config


CONFIG = load_config()
