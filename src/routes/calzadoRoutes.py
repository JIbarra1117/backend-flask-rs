from flask import Blueprint, jsonify, request
from models.calzadoModel import calzados as CalzadoDeportivo
from datetime import datetime, timedelta
from bson import (
    json_util,
)  # Importa json_util desde bson para manejar la serialización de ObjectId

calzado_routes = Blueprint("calzado_routes", __name__)


@calzado_routes.route("/", methods=["GET"])
def obtener_calzados():
    try:
        calzados = CalzadoDeportivo.objects().to_json()
        return jsonify(calzados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/total_por_marca", methods=["GET"])
def total_por_marca():
    try:
        marca = request.args.get("marca")
        if not marca:
            return (
                jsonify({"error": 'Se requiere el parámetro "marca" en la consulta.'}),
                400,
            )

        total_por_marca = CalzadoDeportivo.objects(marca=marca).count()
        return jsonify({"total": total_por_marca})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/marcas", methods=["GET"])
def obtener_marcas():
    try:
        marcas = CalzadoDeportivo.objects.distinct("marca")
        marcas_ordenadas = sorted(marcas, key=lambda x: x.lower())
        return jsonify({"marcas": marcas_ordenadas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/precios", methods=["GET"])
def obtener_precios():
    try:
        precios = CalzadoDeportivo.objects.distinct("precio")
        precios_en_decimales = [float(precio.replace("$", "")) for precio in precios]
        return jsonify({"preciosEnDecimales": precios_en_decimales})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/precios_por_marca", methods=["GET"])
def precios_por_marca():
    try:
        marca = request.args.get("marca")

        if not marca:
            return (
                jsonify({"error": 'Se requiere el parámetro "marca" en la consulta.'}),
                400,
            )

        precios_y_cantidad = CalzadoDeportivo.objects(marca=marca).aggregate(
            [
                {"$group": {"_id": "$precio", "cantidad": {"$sum": 1}}},
                {"$project": {"_id": 0, "precio": "$_id", "cantidad": 1}},
                {"$sort": {"precio": 1}},
            ]
        )

        resultados = [
            {"precio": float(item["precio"]), "cantidad": item["cantidad"]}
            for item in precios_y_cantidad
        ]

        return jsonify({"resultados": resultados})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/productos_por_marca", methods=["GET"])
def productos_por_marca():
    try:
        marca = request.args.get("marca")

        if not marca:
            return (
                jsonify({"error": 'Se requiere el parámetro "marca" en la consulta.'}),
                400,
            )

        productos_por_marca = CalzadoDeportivo.objects(marca=marca)

        if not productos_por_marca:
            return (
                jsonify(
                    {"error": f"No se encontraron productos para la marca: {marca}."}
                ),
                404,
            )
        # Convertir el resultado a una lista de diccionarios
        resultados = serializarProducto(productos_por_marca)
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/producto_por_modelo/<modelo>", methods=["GET"])
def producto_por_modelo(modelo):
    try:
        producto = CalzadoDeportivo.objects(modelo=modelo).first()

        if not producto:
            return jsonify({"error": "Producto no encontrado."}), 404

        # Convertir el objeto a un diccionario antes de devolverlo
        producto_dict = {
            "modelo": producto.modelo,
            "marca": producto.marca,
            "precio": producto.precio,
            "color": producto.color,
            "url_raiz": producto.url_raiz,
            "url_calzado": producto.url_calzado,
            "descripcion": producto.descripcion,
            "calificacion": producto.calificacion,
            "tallas": producto.tallas,
            "imagenes": producto.imagenes,
            "fecha": producto.fecha,
        }

        return jsonify(producto_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/numero_calzados_por_marca", methods=["GET"])
def numero_calzados_por_marca():
    try:
        result = CalzadoDeportivo.objects.aggregate(
            [
                {"$group": {"_id": "$marca", "numeroCalzados": {"$sum": 1}}},
                {"$project": {"_id": 0, "marca": "$_id", "numeroCalzados": 1}},
            ]
        )

        # Convertir el resultado a una lista antes de ordenarla alfabéticamente
        result_list = list(result)

        # Ordenar la lista alfabéticamente por la clave "marca"
        result_list.sort(key=lambda x: x["marca"])

        return jsonify(result_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/top25", methods=["GET"])
def top25():
    try:
        result = CalzadoDeportivo.objects.aggregate(
            [
                {"$sort": {"calificacion": -1}},
                {"$group": {"_id": "$marca", "productos": {"$push": "$$ROOT"}}},
                {
                    "$project": {
                        "marca": "$_id",
                        "_id": 0,
                        "productos": {"$slice": ["$productos", 25]},
                    }
                },
            ]
        )

        # Convertir ObjectId a cadenas en el resultado
        result_list = [
            {
                "marca": item["marca"],
                "productos": [
                    {**product, "_id": str(product["_id"])}
                    for product in item["productos"]
                ],
            }
            for item in result
        ]

        return jsonify(result_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/mejores_productos_por_marca", methods=["GET"])
def mejores_productos_por_marca():
    try:
        marca_parametro = request.args.get("marca")

        if not marca_parametro:
            return jsonify({"error": "La marca es un parámetro requerido."}), 400

        # Consulta los mejores 5 productos directamente sin necesidad de agrupación
        result = (
            CalzadoDeportivo.objects(marca=marca_parametro)
            .order_by("-calificacion")
            .limit(15)
        )

        # Convertir el cursor a una lista de diccionarios
        result_list = serializarProducto(result)

        if not result_list:
            return (
                jsonify(
                    {
                        "error": f"No se encontraron productos para la marca: {marca_parametro}."
                    }
                ),
                404,
            )
        return jsonify(result_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/productos_nuevos", methods=["GET"])
def productos_nuevos():
    try:
        productos_nuevos = CalzadoDeportivo.objects(calificacion=-1)

        if not productos_nuevos:
            return jsonify({"error": "No se encontraron productos nuevos."}), 404

        productos_nuevos_por_marca = {}
        for producto in productos_nuevos:
            marca = producto.marca
            if marca not in productos_nuevos_por_marca:
                productos_nuevos_por_marca[marca] = []

            if len(productos_nuevos_por_marca[marca]) < 25:
                productos_nuevos_por_marca[marca].append(producto)

        resultado_formateado = [
            {"marca": marca, "productos": productos}
            for marca, productos in productos_nuevos_por_marca.items()
        ]

        return jsonify(resultado_formateado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/productos_nuevos_por_marca", methods=["GET"])
def productos_nuevos_por_marca():
    try:
        marca = request.args.get("marca")

        if not marca:
            return (
                jsonify(
                    {
                        "error": "Se debe proporcionar la marca como parámetro de consulta."
                    }
                ),
                400,
            )

        productos_nuevos_por_marca = CalzadoDeportivo.objects(
            marca=marca, calificacion=-1
        )

        if not productos_nuevos_por_marca:
            return jsonify({"marca": marca, "productos": []})

        results = serializarProducto(productos_nuevos_por_marca)

        # Convierte ObjectId a cadenas en los resultados
        results = json_util.loads(json_util.dumps(results))

        return jsonify({"marca": marca, "productos": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/productos_en_fecha", methods=["GET"])
def productos_en_fecha():
    try:
        fecha = request.args.get("fecha")

        if not fecha:
            return (
                jsonify(
                    {
                        "error": "Se debe proporcionar la fecha como parámetro de consulta."
                    }
                ),
                400,
            )

        fecha_objeto = datetime.strptime(fecha, "%Y-%m-%d")
        fecha_sin_hora = datetime(
            fecha_objeto.year, fecha_objeto.month, fecha_objeto.day
        )

        resultados = CalzadoDeportivo.objects(
            fecha__gte=fecha_sin_hora, fecha__lt=fecha_sin_hora + timedelta(days=1)
        )

        hay_productos_en_fecha = len(resultados) > 0

        return jsonify({"hayProductosEnFecha": hay_productos_en_fecha})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calzado_routes.route("/total_calzados", methods=["GET"])
def total_calzados():
    try:
        total_calzados = CalzadoDeportivo.objects.count()
        return jsonify({"total_calzados": total_calzados})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def serializarProducto(productos):
    resultados = [
        {
            "modelo": producto.modelo,
            "precio": producto.precio,
            "modelo": producto.modelo,
            "marca": producto.marca,
            "precio": producto.precio,
            "color": producto.color,
            "url_raiz": producto.url_raiz,
            "url_calzado": producto.url_calzado,
            "descripcion": producto.descripcion,
            "calificacion": producto.calificacion,
            "tallas": producto.tallas,
            "imagenes": producto.imagenes,
            "fecha": producto.fecha,
            "_id": str(producto.id),
        }
        for producto in productos
    ]
    return resultados
