import mongoengine


mongoengine.connect('kek')


class Company(mongoengine.Document):
    name = mongoengine.StringField(required=True, unique=True)
    mail = mongoengine.EmailField(required=True, unique=True)
    cities = mongoengine.ListField(mongoengine.StringField(), required=True)


class User(mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    password = mongoengine.StringField(required=True)
    is_admin = mongoengine.BooleanField()
    staff = mongoengine.ReferenceField(Company)
    mail = mongoengine.EmailField(required=True, unique=True)


class Furniture(mongoengine.Document):
    seller = mongoengine.ReferenceField(Company)
    name = mongoengine.StringField(required=True)
    price = mongoengine.IntField(required=True)
    texture = mongoengine.FileField(required=True)
    photo = mongoengine.FileField(required=True)
    uuid = mongoengine.UUIDField(required=True)
