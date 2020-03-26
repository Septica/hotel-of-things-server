import sys
import os
from operator import itemgetter
import sqlite3

from flask import Flask, request, abort, jsonify


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def create_database_connection():
        return sqlite3.connect(app.config["DATABASE"])

    try:
        with create_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS active_device (room_number TEXT, bluetooth_address TEXT, PRIMARY KEY (room_number, bluetooth_address)) WITHOUT ROWID')
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS customer_state (bluetooth_address TEXT PRIMARY KEY, state TEXT) WITHOUT ROWID')
            conn.commit()
    except:
        print("Unexpected error:", sys.exc_info())
        sys.exit(1)

    @app.route('/')
    def ping():
        return ''

    @app.route('/rooms/<room_number>', methods=['GET'])
    def get_room_details(room_number):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT room_number, group_concat(bluetooth_address) FROM active_device WHERE room_number = ?', (room_number))
                room_number, bluetooth_addresses = cursor.fetchone()
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            if room_number is None:
                abort(404)
            return jsonify({
                'room_number': room_number,
                'bluetooth_addresses': bluetooth_addresses.split(',')
            })

    @app.route('/rooms/<room_number>', methods=['POST'])
    def connect_device_to_a_room(room_number):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO active_device VALUES (?, ?)',
                               (room_number, request.form["bluetooth_address"]))
                cursor.execute('INSERT OR IGNORE INTO customer_state VALUES (?, ?)',
                               (request.form["bluetooth_address"], 'CHECK_IN'))
                conn.commit()
                cursor.execute(
                    'SELECT room_number, group_concat(bluetooth_address) FROM active_device WHERE room_number = ?', room_number)
                room_number, bluetooth_addresses = cursor.fetchone()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return jsonify({
                "room_number": room_number,
                "bluetooth_addresses": bluetooth_addresses.split(",")
            })

    @app.route('/rooms/<room_number>', methods=['DELETE'])
    def disconnect_all_devices_from_a_room(room_number):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM active_device WHERE room_number = ?', (room_number))
                conn.commit()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return str(cursor.rowcount)

    @app.route('/rooms/<room_number>/<bluetooth_address>', methods=['DELETE'])
    def disconnect_device_from_a_room(room_number, bluetooth_address):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM active_device WHERE room_number = ? AND bluetooth_address = ?', (room_number, bluetooth_address))
                conn.commit()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return str(cursor.rowcount)

    @app.route('/devices/<bluetooth_address>', methods=['GET'])
    def get_device_details(bluetooth_address):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT bluetooth_address, group_concat(room_number) FROM active_device WHERE bluetooth_address = ?', (bluetooth_address))
                bluetooth_address, room_numbers = cursor.fetchone()
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            if bluetooth_address is None:
                abort(404)
            return jsonify({
                'bluetooth_address': bluetooth_address,
                'room_numbers': room_numbers.split(',')
            })

    @app.route('/devices/<bluetooth_address>', methods=['PUT'])
    def update_customer_state(bluetooth_address):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE customer_state SET state = ? WHERE bluetooth_address = ?', (request.form["state"], bluetooth_address))
                conn.commit()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return str(cursor.rowcount)

    @app.route('/devices/<bluetooth_address>', methods=['DELETE'])
    def disable_device(bluetooth_address):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM active_device WHERE bluetooth_address = ?', (bluetooth_address))
                cursor.execute(
                    'DELETE FROM customer_state WHERE bluetooth_address = ?', (bluetooth_address))
                conn.commit()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return str(cursor.rowcount)

    return app
