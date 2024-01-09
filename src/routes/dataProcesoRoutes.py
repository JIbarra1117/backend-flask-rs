from flask import Blueprint, jsonify
from models.procesoScrapyModel import procesos as ProcesoScrapy

data_proceso_routes = Blueprint('data_proceso_routes', __name__)

@data_proceso_routes.route('/ultimoProceso', methods=['GET'])
def ultimo_proceso():
    try:
        ultimo_proceso = ProcesoScrapy.objects().order_by('-fecha').first()
        if ultimo_proceso:
            dict = {
                "estado":ultimo_proceso.estado,
                "resultado":ultimo_proceso.resultado,
                "fecha":ultimo_proceso.fecha
            }
            return jsonify(dict)
        else:
            return jsonify({"mensaje": 'No hay procesos almacenados'}), 404
    except Exception as e:
        return jsonify({"mensaje": 'Error al obtener el último proceso', "error": str(e)}), 500
