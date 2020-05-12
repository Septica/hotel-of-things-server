import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from threading import Thread
import bluetooth

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
client_sock=""





def init_bt(current_state,server_sock,client_sock):
  port = 1
  server_sock.bind(("F8:59:71:9A:19:C8",port))
  server_sock.listen(1)
  client_sock,address = server_sock.accept()
  print("Accepted connection from ",address)
  client_sock.send(current_state)
app = Flask(__name__)
CORS(app)

STATE_ENUM = {"deep_sleep", "light_sleep", "awake"}
global current_state
current_state = "awake"
@app.route('/', methods=['POST'])
def change_sleep_state():
    
    if (not request.json) or (request.json['state'] not in STATE_ENUM):
        return jsonify({
            "success": False
        })
    state = request.json['state']
    # Call function to change state in device here
    print(state)
    client_sock.send(state)
    return jsonify({
        "success": True
    })
@app.route('/init', methods=['GET'])
def init():
    thread_bluetooth = Thread(target=init_bt, args=(current_state,server_sock,client_sock,))
    thread_bluetooth.start()
    return jsonify({
        "success": True
    })



if __name__ == '__main__':
    app.run(debug=True, port=5000)
    