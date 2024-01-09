from mongoengine import Document, StringField, BooleanField, DateTimeField, IntField

class procesos(Document):
    # Se agraga la propiedad strict ya que no se requieren todos los campos del documento
    meta = {
    'strict': False,
    }
    estado = StringField()
    resultado = BooleanField()
    fecha = DateTimeField()
