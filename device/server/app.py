import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

STATE_ENUM = {"deep_sleep", "light_sleep", "awake"}

@app.route('/', methods=['POST'])
def change_sleep_state():
    if (not request.json) or (request.json['state'] not in STATE_ENUM):
        return jsonify({
            "success": False
        })
    state = request.json['state']
    # Call function to change state in device here

    return jsonify({
        "success": True
    })


if __name__ == '__main__':
    app.run(debug=True)