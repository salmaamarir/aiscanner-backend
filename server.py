from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, Scan
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aiscanner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key' # Change this in production

db.init_app(app)
jwt = JWTManager(app)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token, userId=user.id), 200

@app.route('/api/scans', methods=['POST'])
@jwt_required()
def add_scan():
    data = request.json
    user_id = get_jwt_identity()

    new_scan = Scan(
        userId=user_id,
        label=data.get('label'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        imageBase64=data.get('imageBase64')
    )
    db.session.add(new_scan)
    db.session.commit()

    return jsonify({"message": "Scan saved", "id": new_scan.id}), 201

@app.route('/api/scans/<int:userId>', methods=['GET'])
@jwt_required()
def get_scans(userId):
    current_user_id = get_jwt_identity()
    if current_user_id != userId:
        return jsonify({"message": "Unauthorized"}), 403

    scans = Scan.query.filter_by(userId=userId).all()
    return jsonify([scan.to_dict() for scan in scans]), 200

@app.route('/api/scans/<int:scanId>', methods=['DELETE'])
@jwt_required()
def delete_scan(scanId):
    current_user_id = get_jwt_identity()
    scan = Scan.query.get(scanId)

    if not scan:
        return jsonify({"message": "Scan not found"}), 404

    if scan.userId != current_user_id:
        return jsonify({"message": "Unauthorized"}), 403

    db.session.delete(scan)
    db.session.commit()
    return jsonify({"message": "Scan deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
