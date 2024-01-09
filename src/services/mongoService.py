from mongoengine import connect
from utils.mensajesFormatos import printInfoSuccesful,printWarning

def configure_mongo(app):
    # Configura la conexión a MongoDB utilizando la configuración de la aplicación Flask
    app.config['MONGODB_SETTINGS'] = {
        'db': 'calzado_deportivo',
        'host': 'mongodb+srv://colis90:uiMQv55mZZ31lX21@cluster0.xuwpdxk.mongodb.net/?retryWrites=true&w=majority',
        'port': 27017,
    }

    try:
        # Llama a connect para establecer la conexión
        connect(
            db=app.config['MONGODB_SETTINGS']['db'],
            host=app.config['MONGODB_SETTINGS']['host'],
            # port=app.config['MONGODB_SETTINGS']['port'],
        )
        printInfoSuccesful(message="Conexión a la base de datos exitosa!")
    except Exception as e:
        printWarning(message="Conexión a la base de datos exitosa!",color='red')
        print(f'Error: {e}')