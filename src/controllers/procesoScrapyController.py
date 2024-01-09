from routes.procesoScrapyRoutes import almacenar_proceso_scrapy
from utils.mensajesFormatos import printInfoSuccesful, printWarning

def handle_scrapy_message(message_data):
    if message_data['estado'] == 'iniciado':
        printInfoSuccesful('Proceso de Scrapy iniciado')
        try:
            almacenar_proceso_scrapy('Iniciado', True)
        except Exception as error:
            printWarning('Error al almacenar el proceso iniciado en MongoDB:', error)
    elif message_data['estado'] == 'completado':
        printInfoSuccesful('Proceso de Scrapy terminado')
        try:
            almacenar_proceso_scrapy('Terminado', False)
        except Exception as error:
            printWarning('Error al almacenar el proceso terminado en MongoDB:', error)