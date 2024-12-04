from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    default_limits=["100 per day"],
)

# Загрузка данных из файла data.json
data_file = 'data.json'
data = {}

if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        data = json.load(f)

def save_data():
    with open(data_file, 'w') as f:
        json.dump(data, f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/set', methods=['POST'])
@limiter.limit("10 per minute")
def set_value():
    key = request.json.get('key')
    value = request.json.get('value')
    
    data[key] = value
    save_data()
    return jsonify({"message": "Key saved"}), 201

@app.route('/get/<key>', methods=['GET'])
def get_value(key):
    value = data.get(key)
    if value is not None:
        return jsonify({"key": key, "value": value}), 200
    return jsonify({"error": "Key not found"}), 404

@app.route('/delete/<key>', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_key(key):
    if key in data:
        del data[key]
        save_data()
        return jsonify({"message": "Key deleted"}), 200
    return jsonify({"error": "Key not found"}), 404

@app.route('/exists/<key>', methods=['GET'])
def exists_key(key):
    exists = key in data
    if exists:
        return jsonify({"message": f"Key '{key}' exists."}), 200
    else:
        return jsonify({"message": f"Key '{key}' doesn't exists."}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)  


