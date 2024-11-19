from cosy.config import CONFIG
from cosy import app, fs_observer


def run() -> None:
    """
    Run the COSY application.
    """
    fs_observer.start()

    run(app.run(host="0.0.0.0", port=CONFIG["internal_api_settings"]["port"]))


if __name__ == "__main__":
    run()
