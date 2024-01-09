from mongoengine import Document, StringField, IntField, ListField, DateTimeField, ObjectIdField

class calzados(Document):
    __id: ObjectIdField()
    modelo = StringField()
    marca = StringField()
    precio = IntField()
    color = StringField()
    url_raiz = StringField()
    url_calzado = StringField()
    descripcion = StringField()
    calificacion = IntField()
    tallas = ListField()
    imagenes = ListField()
    fecha = DateTimeField()
