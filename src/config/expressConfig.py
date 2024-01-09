from flask_cors import CORS
from config.config import Config


def configure_app(app):
    app.config.from_object(Config)

    # Configurar CORS si es necesario
    if app.config["CORS_ENABLED"]:
        CORS(
            app,
            resources={
                r"/*": {"origins": "*"},
                r"/socket.io/*": {"origins": "*"},
            },
        )

    return app
