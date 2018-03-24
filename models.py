import mongoengine


mongoengine.connect('kek')


class Company(mongoengine.Document):
    name = mongoengine.StringField(required=True, unique=True)
    company_name = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    furniture = mongoengine.ListField(mongoengine.ReferenceField('Furniture'))
    categories = mongoengine.ListField(mongoengine.ReferenceField('Category'))
    cities = mongoengine.ListField(mongoengine.StringField(), required=True)
    label = mongoengine.ReferenceField('FileModel')


class FileModel(mongoengine.Document):
    file = mongoengine.FileField(required=True)


class Furniture(mongoengine.Document):
    seller = mongoengine.ReferenceField(Company)
    name = mongoengine.StringField(required=True)
    category = mongoengine.ReferenceField('Category')
    price = mongoengine.IntField(required=True)
    graphic_model = mongoengine.ReferenceField(FileModel)
    preview = mongoengine.ReferenceField(FileModel)


class Category(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    companies = mongoengine.ListField(mongoengine.ReferenceField(Company))
    furniture = mongoengine.ListField(mongoengine.ReferenceField(Furniture))
