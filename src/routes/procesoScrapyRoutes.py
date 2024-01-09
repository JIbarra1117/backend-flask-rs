from datetime import datetime
from models.procesoScrapyModel import procesos as ProcesoScrapy
from utils.mensajesFormatos import printInfoSuccesful, printWarning

def almacenar_proceso_scrapy(estado, resultado):
    try:
        fecha_actual = datetime.utcnow()

        # Crear una nueva instancia del modelo ProcesoScrapy
        nuevo_proceso = ProcesoScrapy(
            estado=estado,
            resultado=resultado,
            fecha=fecha_actual
        )

        # Guardar en la base de datos
        nuevo_proceso.save()

        printInfoSuccesful('Proceso de Scrapy almacenado exitosamente en MongoDB')
    except Exception as error:
        printWarning('Error al almacenar el proceso de Scrapy en MongoDB:', error)
        raise error