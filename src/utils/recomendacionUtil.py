import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import re
from nltk.corpus import stopwords
from models.calzadoModel import calzados
import json


def quitar_numeros(string_argumento):
    """
    Función que toma un string y quita
    los números utilizando una expresión
    regular. También convierte todos los
    caracteres a minúscula
    """
    string_argumento = string_argumento.lower()
    string_argumento = re.sub(r"\d+", "", string_argumento)
    return string_argumento


def serializarProducto(productos):
    resultados = [
        {
            "modelo": producto["modelo"],
            "precio": producto["precio"],
            "modelo": producto["modelo"],
            "marca": producto["marca"],
            "precio": producto["precio"],
            "color": producto["color"],
            "url_raiz": producto["url_raiz"],
            "url_calzado": producto["url_calzado"],
            "descripcion": producto["descripcion"],
            "calificacion": producto["calificacion"],
            "tallas": producto["tallas"],
            "imagenes": producto["imagenes"],
            "fecha": producto["fecha"],
            "_id": str(producto["_id"]["$oid"]),
        }
        for producto in productos
    ]
    return resultados


## Obtener todos los calzados deportivos
def guardarTablaSimilitudPorCoseno():
    calzadosDeportivos = serializarProducto(json.loads(calzados.objects().to_json()))
    data = list(calzadosDeportivos)

    # Crear DataFrame
    df = pd.DataFrame(data)

    # Convertir la columna 'tallas' a una lista plana
    lista_planar = [item for sublist in df["tallas"] for item in sublist]

    # Crear un conjunto para eliminar duplicados
    conjunto_unico = set(lista_planar)

    # Convertir el conjunto nuevamente a una lista
    lista_unicos = list(conjunto_unico)

    # Mostrar la lista sin duplicados
    # print(len(lista_unicos))
    tallas = pd.DataFrame(sorted(lista_unicos))

    # Guardar el DataFrame en un archivo Excel
    nombre_archivo = "tallas_diferentes.xlsx"
    tallas.to_excel(nombre_archivo, index=False)

    # Combina las características de texto en una sola columna
    df["text_features"] = (
        df[["color", "modelo", "marca"]]
        .astype(str)
        .apply(lambda x: " ".join(x), axis=1)
    )
    # df['text_features'] = df[['marca', 'color']].astype(str).apply(lambda x: ' '.join(x), axis=1)
    df["text_features"] = df["text_features"].apply(quitar_numeros)
    df["text_features"] = (
        df[["text_features", "tallas"]].astype(str).apply(lambda x: " ".join(x), axis=1)
    )

    # Detectar stop-words
    stop_words = set(stopwords.words("english"))
    # Aplica TF-IDF a las características de texto
    tfidf_vectorizer = TfidfVectorizer(
        stop_words=list(stop_words), min_df=10, max_df=0.85
    )
    tfidf_matrix = tfidf_vectorizer.fit_transform(df["text_features"])

    # Calcula la similitud del coseno
    cosine_similarities_dev = linear_kernel(tfidf_matrix)
    
    


def obtenerRecomendaciones(listaProductoPorId):
    return ""