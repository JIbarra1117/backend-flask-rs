# from bson import ObjectId  # Necesario para trabajar con IDs de MongoDB
# from flask import Blueprint, jsonify, request
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import linear_kernel
# import pandas as pd
# import re
# from pymongo import MongoClient

# # Crear un Blueprint en Flask para organizar rutas y funciones
# recomendaciones_routes = Blueprint("recomendaciones", __name__)


# # Función para quitar números de un texto
# def quitar_numeros(string_argumento):
#     string_argumento = string_argumento.lower()
#     string_argumento = re.sub(r"\d+", "", string_argumento)
#     return string_argumento


# # Conexión a MongoDB y creación del DataFrame
# client = MongoClient(
#     "mongodb+srv://colis90:uiMQv55mZZ31lX21@cluster0.xuwpdxk.mongodb.net/?retryWrites=true&w=majority"
# )
# database = client["calzado_deportivo"]
# collection = database["calzados"]

# cursor = collection.find({})
# df = pd.DataFrame(list(cursor))

# # Combinar características de texto en una columna y eliminar números
# df["text_features"] = (
#     df[["color", "modelo", "descripcion", "precio"]]
#     .astype(str)
#     .apply(lambda x: " ".join(x), axis=1)  # , "marca"
# )
# df["text_features"] = df["text_features"].apply(quitar_numeros)

# # Detectar stop-words
# # stop_words = set(stopwords.words("english"))

# # Aplicar TF-IDF a las características de texto
# tfidf_vectorizer = TfidfVectorizer(stop_words="english", min_df=10, max_df=0.85)
# tfidf_matrix = tfidf_vectorizer.fit_transform(df["text_features"])

# # Calcular la similitud del coseno
# cosine_similarities = linear_kernel(tfidf_matrix)


# # Función para obtener recomendaciones basadas en productos seleccionados
# def get_recommendations(selected_product_ids, cosine_similarities):
#     try:
#         # Obtener índices de productos seleccionados
#         selected_indices = [
#             df[df["_id"] == ObjectId(product_id)].index[0]
#             for product_id in selected_product_ids
#         ]
#         # Calcular la similitud promedio
#         avg_cosine_similarities = cosine_similarities[selected_indices].mean(axis=0)
#         sim_scores = list(enumerate(avg_cosine_similarities))
#         # Ordenar productos por similitud
#         sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#         sim_scores = sim_scores[
#             1:61
#         ]  # Top 50 recomendaciones, excluyendo los productos seleccionados

#         # Obtener índices y puntajes de similitud
#         product_indices = [i[0] for i in sim_scores]
#         similarity_scores = [i[1] for i in sim_scores]

#         # Crear DataFrame con las recomendaciones
#         recommendations_df = df.iloc[product_indices].copy()
#         recommendations_df["similarity_score"] = similarity_scores

#         # Ordenar recomendaciones por marca y similitud
#         recommendations_df = recommendations_df.sort_values(
#             by=["marca", "similarity_score"], ascending=[True, False]
#         )

#         # Convertir la columna '_id' a cadena (texto)
#         recommendations_df["_id"] = recommendations_df["_id"].apply(lambda x: str(x))

#         # Obtener el JSON con la opción 'orient="records"'
#         recommendations_json = recommendations_df.to_json(orient="records")

#         return recommendations_json
#     except Exception as e:
#         print(f"Error en obtener recomendacion: {e}")
#         return jsonify({"error": str(e)}), 500  # Devuelve un error como JSON


# # Ruta en Flask para obtener recomendaciones por IDs de productos
# @recomendaciones_routes.route("/recomendacionesByIds", methods=["GET"])
# def obtener_recomendaciones():
#     try:
#         # Obtener IDs de productos de la solicitud
#         selected_ids = request.args.getlist("ids")
#         # print(selected_ids)
#         # Obtener recomendaciones llamando a la función
#         recommendations = get_recommendations(selected_ids, cosine_similarities)
#         # Devolver las recomendaciones en formato JSON
#         return recommendations
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500  # Devuelve un error como JSON

from bson import ObjectId
from flask import Blueprint, jsonify, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import re
from pymongo import MongoClient

recomendaciones_routes = Blueprint("recomendaciones", __name__)

# Conexión a MongoDB y creación del DataFrame
client = MongoClient(
    "mongodb+srv://colis90:uiMQv55mZZ31lX21@cluster0.xuwpdxk.mongodb.net/?retryWrites=true&w=majority"
)
database = client["calzado_deportivo"]
collection = database["calzados"]


# Función para quitar números de un texto
def quitar_numeros(string_argumento):
    return re.sub(r"\d+", "", string_argumento.lower())


# Crear DataFrame y características de texto
cursor = collection.find({})
df = pd.DataFrame(list(cursor))
df["text_features"] = (
    df[["color", "modelo", "descripcion", "precio"]]
    .astype(str)
    .apply(lambda x: " ".join(x), axis=1)
    .apply(quitar_numeros)
)

# Aplicar TF-IDF a las características de texto
tfidf_vectorizer = TfidfVectorizer(stop_words="english", min_df=10, max_df=0.85) # Este metodo tiene predefinido la implementacion de NLP
tfidf_matrix = tfidf_vectorizer.fit_transform(df["text_features"])
cosine_similarities = linear_kernel(tfidf_matrix)


# Función para obtener recomendaciones
def get_recommendations(selected_product_ids, cosine_similarities, df):
    try:
        selected_indices = [
            df[df["_id"] == ObjectId(product_id)].index[0]
            for product_id in selected_product_ids
        ]
        avg_cosine_similarities = cosine_similarities[selected_indices].mean(axis=0)
        sim_scores = sorted(
            enumerate(avg_cosine_similarities), key=lambda x: x[1], reverse=True
        )[1:61]

        product_indices, similarity_scores = zip(*sim_scores)
        recommendations_df = df.iloc[list(product_indices)].copy()
        recommendations_df["similarity_score"] = similarity_scores

        recommendations_df = recommendations_df.sort_values(
            by=["marca", "similarity_score"], ascending=[True, False]
        )

        recommendations_df["_id"] = recommendations_df["_id"].astype(str)
        return recommendations_df.to_json(orient="records")
    except Exception as e:
        print(f"Error en obtener recomendacion: {e}")
        return jsonify({"error": str(e)}), 500


# Ruta en Flask para obtener recomendaciones por IDs de productos
@recomendaciones_routes.route("/recomendacionesByIds", methods=["GET"])
def obtener_recomendaciones():
    try:
        selected_ids = request.args.getlist("ids")
        recommendations = get_recommendations(selected_ids, cosine_similarities, df)
        return recommendations
    except Exception as e:
        return jsonify({"error": str(e)}), 500
