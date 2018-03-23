from flask import Flask, jsonify, send_file, request
from models import Company, Furniture
from uuid import uuid4


def create_app():
    application = Flask(__name__)
    return application


app = create_app()


@app.route('/companies', methods=['GET'])
def get_companies():
    response = {'companies': []}
    for comp in Company.objects:
        response['companies'].append({
            'name': comp.name,
            'mail': comp.mail,
            'cities': comp.cities
        })
    return jsonify(response)


@app.route('/company/<string:name>', methods=['GET'])
def get_company(name):
    comp = Company.objects(name=name).first()
    response = {'companies': []}
    response['companies'].append({
        'name': comp.name,
        'mail': comp.mail,
        'cities': comp.cities
    })
    return jsonify(response)


@app.route('/company', methods=['POST'])
def post_company():
    json = request.get_json()
    comp = Company(name=json['name'])
    comp.mail = json['mail']
    comp.cities = json['cities']
    comp.save()
    return ''


@app.route('/furniture', methods=['GET'])
def all_furniture():
    response = {'furniture': []}
    for furn in Furniture.objects:
        response['furniture'].append({
            'name': furn.name,
            'price': furn.price,
            'seller': furn.seller,
            'uuid': furn.uuid
        })
    return jsonify(response)


@app.route('/furniture/<uuid:_id>', methods=['GET'])
def furniture(_id):
    furn = Furniture.objects(uuid=_id).first()
    response = {'furniture': []}
    response['furniture'].append({
        'name': furn.name,
        'price': furn.price,
        'seller': furn.seller,
        'uuid': furn.uuid
    })
    return jsonify(response)


@app.route('/furniture', methods=['POST'])
def post_furniture():
    files = request.files
    texture = files['texture']
    photo = files['photo']
    json = request.get_json()
    seller = Company.objects(name=json['seller']).first()
    furn = Furniture(seller=seller)
    uuid = uuid4()
    furn.uuid = uuid
    furn.name = json['name']
    furn.price = json['price']
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


@app.route('/furniture/<uuid:_id>/texture', methods=['GET'])
def furniture_texture(_id):
    furn = Furniture.objects(uuid=_id).first()
    texture = furn.texture
    return send_file(texture, mimetype=texture.content_type,
                     attachment_filename=texture.filename,
                     as_attachment=True)


@app.route('/furniture/<uuid:_id>/photo', methods=['GET'])
def furniture_photo(_id):
    furn = Furniture.objects(uuid=_id).first()
    photo = furn.photo
    return send_file(photo, mimetype=photo.content_type,
                     attachment_filename=photo.filename,
                     as_attachment=True)


if __name__ == '__main__':
    app.run()
