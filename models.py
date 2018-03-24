import mongoengine


mongoengine.connect('kek')


class Company(mongoengine.Document):
    name = mongoengine.StringField(required=True, unique=True)
    company_name = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    categories = mongoengine.ListField(mongoengine.StringField())
    cities = mongoengine.ListField(mongoengine.StringField(), required=True)


class FileModel(mongoengine.Document):
    file = mongoengine.FileField(required=True)


class Furniture(mongoengine.Document):
    seller = mongoengine.ReferenceField(Company)
    name = mongoengine.StringField(required=True)
    category = mongoengine.StringField(required=True)
    price = mongoengine.IntField(required=True)
    graphic_model = mongoengine.ReferenceField(FileModel)
    preview = mongoengine.ReferenceField(FileModel)
