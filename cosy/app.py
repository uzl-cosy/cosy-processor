from flask import Flask, Blueprint
from flask_cors import CORS
import signal
import os
from types import FrameType


def signal_handler(sig: signal.Signals, frame: FrameType) -> None:
    """
    Signal handler to exit the program.
    """
    print(sig)
    print(type(frame))
    os._exit(1)


def create_app(bp: Blueprint) -> Flask:
    """
    Create a Flask app with the specified blueprint and enable CORS.

    :param bp: Blueprint to register with the app
    :return: Flask app
    """

    app = Flask(__name__)
    CORS(app)
    app.logger = None
    app.register_blueprint(bp)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    return app
