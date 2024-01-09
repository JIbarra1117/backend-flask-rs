from controllers.procesoScrapyController import handle_scrapy_message
from utils.mensajesFormatos import printWarning

def handle_websocket_message(message_data):
    if message_data:
        # printInfoSuccesful(f'Mensaje WebSocket recibido: {message_data}')

        # Verifica el tipo de mensaje y llama al controlador adecuado
        if message_data['tipo'] == 'scrapy':
            handle_scrapy_message(message_data)
        # Agrega más casos según sea necesario para otros tipos de mensajes
        else:
            printWarning(f'Tipo de mensaje no reconocido: {message_data["tipo"]}')
