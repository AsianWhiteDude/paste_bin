import logging

from flask import Flask, jsonify
from utils import get_key
from tasks import create_hash_keys

app = Flask(__name__)

create_hash_keys.delay()

@app.route('/get_hash_key', methods=['GET'])
def get_hash_key():

    hash_key = get_key()

    return jsonify({'hash_key': hash_key})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
