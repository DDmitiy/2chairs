from flask import Flask, jsonify, send_file, request
from models import Company, Furniture, FileModel, Category
from hashlib import md5
from flask_cors import CORS, cross_origin
import jwt
import datetime

TOKEN_EXPIRED = 0
TOKEN_INVALID = 1

app = Flask(__name__)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, expose_headers=['Content-Disposition'])


def encode_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(
        payload,
        'aaa',
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


@app.route('/api/companies', methods=['GET'])
def get_companies():
    response = {
        'companies': [{
            'name': c.company_name,
            'label': "/api/company/%s/label" % c.company_name
        } for c in Company.objects]
    }
    return jsonify(response)


@app.route('/api/company/<string:name>', methods=['GET'])
def get_company(name):
    c = Company.objects(name=name).first()
    response = {
        'company': {
            'name': c.company_name,
            'label': "/api/company/%s/label" % c.company_name
        }}
    return jsonify(response)


@app.route('/api/auth/register', methods=['POST'])
@cross_origin()
def new_company():
    json = request.json
    name = json['name']
    company_name = json['company_name']
    password = json['password']
    cities = json['cities']
    company_label = json['company_label']
    company = Company(name=name,
                      company_name=company_name,
                      password=to_md5(password),
                      cities=cities,
                      label=company_label).save()
    return encode_token(company.name)


@app.route('/api/auth/login', methods=['POST'])
@cross_origin()
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
    response = {'furniture': [
            {
                'name': f.name,
                'price': f.price,
                'preview_url': "/api/furniture/%s/preview" % str(f.id),
                'model_url': "/api/furniture/%s/model" % str(f.id),
                'id': str(f.id)
            } for f in Furniture.objects
        ]
    }
    return jsonify(response)


@app.route('/api/furniture/<string:_id>', methods=['GET'])
@cross_origin()
def furniture(_id):
    f = Furniture.objects(id=_id).first()
    response = {'furniture': {
        'name': f.name,
        'price': f.price,
        'preview_url': "/api/furniture/%s/preview" % str(f.id),
        'model_url': "/api/furniture/%s/model" % str(f.id),
        'id': str(f.id)
    }}
    return jsonify(response)


@app.route('/api/furniture', methods=['POST'])
@cross_origin()
def new_furniture():
    json = request.json
    preview_id = json['preview']
    graphic_model_id = json['model']
    preview_file = FileModel(id=preview_id).objects.first()
    graphic_file = FileModel(id=graphic_model_id).objects.first()
    token = json['token']
    category = json['category']
    cat = Category.objects(name=category).first()
    if not cat:
        cat = Category(name=category).save()
    name = decode_token(token)
    if name is TOKEN_EXPIRED and name is TOKEN_INVALID:
        return '', 400
    company = Company.objects(name=name).first()
    company.categories.append(cat)  # FIXME all mongoengine queries
    company.save()
    if not company:
        return '', 400
    furn = Furniture(seller=company,
                     name=json['name'],
                     category=cat,
                     price=json['price'],
                     graphic_model=graphic_file,
                     preview_file=preview_file,
                     ).save()
    company.furniture.append(furn)
    company.save()
    cat.companies.append(company)
    cat.furniture.append(furn)
    cat.save()
    return jsonify({'id': str(furn.id)}), 201


@app.route('/api/files', methods=['POST'])
@cross_origin()
def files():
    if not request.files['file']:
        return '', 400
    file = FileModel()
    file.file.put(request.files['file'],
                  content_type=request.files['file'].content_type,
                  filename=request.files['file'].filename)
    file.save()
    return jsonify({'id': str(file.id)})


@app.route('/api/furniture/<string:_id>', methods=['DELETE'])
@cross_origin()
def delete_furniture(_id):
    json = request.get_json()
    name = decode_token(json['token'])
    if name is TOKEN_INVALID or name is TOKEN_EXPIRED:
        return '', 403
    company = Company.objects(name=name).first()
    furn = Furniture.objects(id=id).first()
    if furn.seller is company:
        furn.delete()
        return ''
    else:
        return '', 403


@app.route('/api/furniture/<string:_id>/preview', methods=['GET'])
@cross_origin()
def furniture_preview(_id):
    furn = Furniture.objects(id=_id).first()
    if not furn:
        return '', 404
    preview = furn.preview.file
    return send_file(preview, mimetype=preview.content_type,
                     attachment_filename=preview.filename,
                     as_attachment=True)


@app.route('/api/furniture/<string:_id>/model', methods=['GET'])
@cross_origin()
def furniture_model(_id):
    furn = Furniture.objects(id=_id).first()
    if not furn:
        return '', 404
    model = furn.graphic_model.file
    return send_file(model, mimetype=model.content_type,
                     attachment_filename=model.filename,
                     as_attachment=True)


@app.route('/api/company/<string:companyname>/label', methods=['GET'])
def company_label(companyname):
    company = Company.objects(company_name=companyname).first()
    if not company:
        return '', 404
    label = company.label.file
    return send_file(label, mimetype=label.content_type,
                     attachment_filename=label.filename,
                     as_attachment=True)


@app.route('/api/categories', methods=['GET'])
@cross_origin()
def get_categories():
    name = request.args.get('name')
    company = Company.objects(name=name).first()
    response = {'categories': []}
    for cat in company.categories:
        furn = cat.furniture.first()
        if furn:
            response['categories'].append({
                'category': cat.name,
                'preview_url': "/api/furniture/%s/preview" % str(furn.id)
            })
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
