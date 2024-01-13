import json
from flask import Flask, request
from flask_socketio import SocketIO

from routes.calzadoRoutes import calzado_routes
from routes.dataProcesoRoutes import data_proceso_routes
from routes.recomendacionRoutes import recomendaciones_routes
from services.mongoService import configure_mongo
from utils.websocketUtil import handle_websocket_message
from utils.mensajesFormatos import printInfoSuccesful, printWarning
from config.expressConfig import configure_app
import time

app = Flask(__name__)
configure_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")
configure_mongo(app)


# Middleware para medir el tiempo de ejecución de las solicitudes
@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    if hasattr(request, "start_time"):
        elapsed_time = time.time() - request.start_time
        elapsed_time_format = (
            f"{elapsed_time * 1000:.2f} ms"
            if elapsed_time < 1
            else f"{elapsed_time:.2f} seg"
        )
        app.logger.info(f"Tiempo de ejecución: {elapsed_time_format}")
    return response


# Registrar los blueprints
app.register_blueprint(calzado_routes, url_prefix="/calzado_deportivo")
# app.register_blueprint(data_proceso_routes, url_prefix="/procesoScrapy")
# app.register_blueprint(recomendaciones_routes, url_prefix="/recomendacion")


# Logica de Websocket
@socketio.on("connect")
def handle_connect():
    keys = ["Scrapy", "React"]
    key_cliente = request.args.get("Key-Cliente")
    mensaje = f"Cliente conectado desde {'Scrapy' if keys[0] == key_cliente else 'Aplicación React'}"
    printInfoSuccesful(mensaje) if key_cliente in keys else printWarning(
        "Intento de conexión no autorizado. Clave compartida incorrecta."
    )
    return key_cliente in keys


@socketio.on("message")
def handle_message(message):
    message_data = json.loads(message)
    handle_websocket_message(message_data)
    socketio.emit("scrapy_message", {"message": message_data})
    # if str(message_data['estado']) == 'completado':
    #     guardarTablaSimilitudPorCoseno()


if __name__ == "__main__":
    socketio.run(app)
