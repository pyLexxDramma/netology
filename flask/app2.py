from functools import wraps

import jwt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    ads = db.relationship('Ad', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Ad {self.title}>'

with app.app_context():
    db.create_all()

def token_required(roles=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = User.query.filter_by(id=data['user_id']).first()
            except:
                return jsonify({'message': 'Token is invalid!'}), 401

            if roles is not None and current_user.role not in roles:
                return jsonify({'message': 'Cannot perform that function!'}), 403

            return f(current_user, *args, **kwargs)

        return decorated
    return decorator

@app.route('/register', methods=['POST'])
@token_required(roles=['admin'])
def register(current_user):
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(email=data['email'], password=hashed_password, role=data.get('role', 'user'))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})

@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()

    if not auth or not auth['email'] or not auth['password']:
        return jsonify({'message': 'Could not verify'}), 401

    user = User.query.filter_by(email=auth['email']).first()

    if not user:
        return jsonify({'message': 'Could not verify'}), 401

    if check_password_hash(user.password, auth['password']):
        token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30), 'role': user.role}, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})

    return jsonify({'message': 'Could not verify'}), 401

@app.route('/ad', methods=['POST'])
@token_required()
def create_ad(current_user):
    data = request.get_json()

    new_ad = Ad(title=data['title'], description=data['description'], user_id=current_user.id)
    db.session.add(new_ad)
    db.session.commit()

    return jsonify({'message': 'Ad created!'})

@app.route('/ad/<int:ad_id>', methods=['PUT'])
@token_required()
def update_ad(current_user, ad_id):
    ad = Ad.query.get_or_404(ad_id)

    if ad.user_id != current_user.id:
        return jsonify({'message': 'Cannot perform that function!'}), 403

    data = request.get_json()
    ad.title = data['title']
    ad.description = data['description']

    db.session.commit()

    return jsonify({'message': 'Ad updated!'})

@app.route('/ad/<int:ad_id>', methods=['DELETE'])
@token_required()
def delete_ad(current_user, ad_id):
    ad = Ad.query.get_or_404(ad_id)

    if ad.user_id != current_user.id:
        return jsonify({'message': 'Cannot perform that function!'}), 403

    db.session.delete(ad)
    db.session.commit()

    return jsonify({'message': 'Ad deleted!'})


@app.route('/admin/test', methods=['GET'])
@token_required(roles=['admin'])
def admin_test(current_user):
    return jsonify({'message': 'Admin route accessed successfully!'})

if __name__ == '__main__':
    app.run(debug=True)