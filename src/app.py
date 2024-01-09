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

socketio = SocketIO(app,cors_allowed_origins="*")

# Configurar conexión a MongoDB
configure_mongo(app)


# Middleware para medir el tiempo de ejecución de las solicitudes
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, "start_time"):
        elapsed_time = time.time() - request.start_time
        if elapsed_time < 1:
            elapsed_time_ms = elapsed_time * 1000
            app.logger.info(f"Tiempo de ejecución: {elapsed_time_ms:.2f} ms")
        else:
            app.logger.info(f"Tiempo de ejecución: {elapsed_time:.2f} seg")
    return response

# Registrar los blueprints
app.register_blueprint(calzado_routes, url_prefix="/calzado_deportivo")
app.register_blueprint(data_proceso_routes, url_prefix="/procesoScrapy")
app.register_blueprint(recomendaciones_routes, url_prefix="/recomendacion")


# Logica de Websocket
@socketio.on("connect")
def handle_connect():
    # keys para cada tipo de conexion
    keys = ["Scrapy", "React"]
    keyCliente = request.args.get("Key-Cliente")
    if keys[0] == str(keyCliente):
        printInfoSuccesful("Cliente conectado desde Scrapy")
    elif keys[1] == str(keyCliente):
        printInfoSuccesful("Cliente conectado desde Aplicación React")
    else:
        printWarning("Intento de conexión no autorizado. Clave compartida incorrecta.")
        return False


@socketio.on("message")
def handle_message(message):
    message_data = json.loads(message)
    # printInfoSuccesful("Mensaje recibido desde Python:", message_data)
    # Utiliza el utilitario de WebSocket para manejar el mensaje
    handle_websocket_message(message_data)
    # Emitir un evento a React con el mensaje de Scrapy
    socketio.emit("scrapy_message", {"message": message_data})
    # if str(message_data['estado'])=='completado':
    #     guardarTablaSimilitudPorCoseno()

    ## Si ya se completo la informacion
if __name__ == "__main__":
    # socketio.run(app)
    socketio.run(app)
