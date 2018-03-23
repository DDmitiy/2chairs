import mongoengine


mongoengine.connect('kek')


class Company(mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    company_name = mongoengine.StringField(required=True, unique=True)
    password = mongoengine.StringField(required=True)
    mail = mongoengine.EmailField(required=True, unique=True)
    cities = mongoengine.ListField(mongoengine.StringField(), required=True)


class Furniture(mongoengine.Document):
    seller = mongoengine.ReferenceField(Company)
    name = mongoengine.StringField(required=True)
    price = mongoengine.IntField(required=True)
    texture = mongoengine.FileField(required=True)
    photo = mongoengine.FileField(required=True)
    uuid = mongoengine.UUIDField(required=True)
