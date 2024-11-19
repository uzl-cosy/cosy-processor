from cosy.app import create_app
from cosy.filesystem import create_filesystem_observer, setup_data_dir
from cosy.handlers.setup import register_handlers
from cosy.recorder import Recorder
from cosy.handlers import create_handlers
from cosy.routes import create_blueprint
from cosy.events import ee

"""
Create the necessary components for the COSY application.
"""

recorder = Recorder()

bp = create_blueprint(ee, recorder)
app = create_app(bp)

handlers = create_handlers()

setup_data_dir()

register_handlers(ee, handlers)

fs_observer = create_filesystem_observer(ee)
