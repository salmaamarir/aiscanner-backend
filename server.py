from flask import Flask, request, jsonify
from database import db, Scan
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aiscanner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/scans', methods=['POST'])
def add_scan():
    data = request.json
    new_scan = Scan(
        userId=str(data.get('userId')),
        label=data.get('label'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        imageBase64=data.get('imageBase64')
    )
    db.session.add(new_scan)
    db.session.commit()
    return jsonify({"message": "Scan saved", "id": new_scan.id}), 201

@app.route('/api/scans/<userId>', methods=['GET'])
def get_scans(userId):
    scans = Scan.query.filter_by(userId=userId).all()
    return jsonify([scan.to_dict() for scan in scans]), 200

@app.route('/api/scans/<int:scanId>', methods=['DELETE'])
def delete_scan(scanId):
    scan = Scan.query.get(scanId)
    if not scan:
        return jsonify({"message": "Scan not found"}), 404
    db.session.delete(scan)
    db.session.commit()
    return jsonify({"message": "Scan deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)