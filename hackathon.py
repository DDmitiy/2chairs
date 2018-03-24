from flask import Flask, jsonify, send_file, request
from models import Company, Furniture
from uuid import uuid4
from hashlib import md5
import jwt
import datetime

TOKEN_EXPIRED = 0
TOKEN_INVALID = 1


def encode_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(
        payload,
        app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )


def to_md5(password):
    return md5(password.encode('utf-8')).hexdigest()


def decode_token(token):
    try:
        payload = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms='HS256')
    except jwt.ExpiredSignatureError:
        return TOKEN_EXPIRED
    except jwt.InvalidTokenError:
        return TOKEN_INVALID
    return payload['username']


def create_app():
    application = Flask(__name__)
    return application


app = create_app()


@app.route('/companies', methods=['GET'])
def get_companies():
    response = {
        'companies': [{
            'name': c.company_name,
            'cities': c.cities
        } for c in Company.objects]
    }
    return jsonify(response)


@app.route('/companies/<string:name>', methods=['GET'])
def get_company(name):
    c = Company.objects(name=name).first()
    response = {
        'company': {
            'name': c.company_name,
            'cities': c.cities
        }}
    return jsonify(response)


@app.route('/api/register', methods=['POST'])
def new_company():
    json = request.json
    name = json['name']
    company_name = json['companyname']
    password = json['password']
    cities = json['cities']
    company = Company(name=name,
                      company_name=company_name,
                      password=to_md5(password),
                      cities=cities).save()
    company.save()
    return encode_token(name)


@app.route('/api/auth/login', methods=['POST'])
def login():
    json = request.json
    name = json['name']
    password = json['password']
    company = Company.objects(name=name, password=to_md5(password)).first()
    if company:
        return encode_token(name)
    else:
        return '', 400


@app.route('/api/furniture', methods=['GET'])
def all_furniture():
    response = {'furniture':
        [{
            'seller': f.seller.companyname,
            'name': f.name,
            'price': f.price,
            'uuid': str(f.uuid)
        } for f in Furniture.objects
        ]
    }
    return jsonify(response)


@app.route('/api/furniture/<uuid:_id>', methods=['GET'])
def furniture(_id):
    f = Furniture.objects(uuid=_id).first()
    response = {'furniture': {
        'seller': f.seller.companyname,
        'name': f.name,
        'price': f.price,
        'uuid': str(f.uuid)
    }}
    return jsonify(response)


@app.route('/api/furniture', methods=['POST'])
def new_furniture():
    files = request.files
    texture = files['texture']
    photo = files['photo']
    json = request.get_json()
    name = decode_token(json['token'])
    if name is TOKEN_EXPIRED or name is TOKEN_INVALID:
        return '', 403
    uuid = uuid4()
    seller = Company.objects(name=name).first()
    furn = Furniture(seller=seller,
                     uuid=uuid,
                     name=json['name'],
                     price=json['price'])
    furn.texture.put(texture,
                     content_type=texture.content_type,
                     filename=texture.filename)
    furn.photo.put(photo,
                   content_type=photo.content_type,
                   filename=photo.filename)
    furn.save()
    return jsonify({
        'uuid': str(uuid)
    })


@app.route('/api/furniture/<uuid:_id>', methods=['DELETE'])
def delete_furniture(_id):
    json = request.get_json()
    name = decode_token(json['token'])
    if name is TOKEN_INVALID or name is TOKEN_EXPIRED:
        return '', 403
    company = Company.objects(name=name).first()
    furn = Furniture.objects(uuid=id).first()
    if furn.seller is company:
        furn.delete()
        return ''
    else:
        return '', 403


@app.route('/api/furniture/<uuid:_id>/texture', methods=['GET'])
def furniture_texture(_id):
    furn = Furniture.objects(uuid=_id).first()
    texture = furn.texture
    return send_file(texture, mimetype=texture.content_type,
                     attachment_filename=texture.filename,
                     as_attachment=True)


@app.route('/api/furniture/<uuid:_id>/photo', methods=['GET'])
def furniture_photo(_id):
    furn = Furniture.objects(uuid=_id).first()
    photo = furn.photo
    return send_file(photo, mimetype=photo.content_type,
                     attachment_filename=photo.filename,
                     as_attachment=True)


@app.route('/categories', methods=['GET'])
def get_categories():
    json = request.json
    name = json['name']
    company = Company.objects(name=name).first()
    response = {}
    for cat in company.categories:
        furn = Furniture.objects(seller=company, category=cat).first()
        response[cat] = "/api/furniture/%s/photo" % str(furn.uuid)
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
