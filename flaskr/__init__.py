import sys
import os
from operator import itemgetter
import sqlite3

from flask import Flask, request, abort, jsonify, send_from_directory


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
        return sqlite3.connect(app.config['DATABASE'])

    try:
        with create_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS room (room_number TEXT PRIMARY KEY) WITHOUT ROWID')
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS active_device (room_number TEXT, mac_address TEXT, PRIMARY KEY (room_number, mac_address)) WITHOUT ROWID')
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS customer_state (mac_address TEXT PRIMARY KEY, state TEXT) WITHOUT ROWID')
            conn.commit()
    except:
        print("Unexpected error:", sys.exc_info())
        sys.exit(1)

    @app.route('/')
    def ping():
        return ''

    @app.route('/rooms', methods=['GET'])
    def get_all_rooms():
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT group_concat(room_number) FROM room')
                rooms, = cursor.fetchone()
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return jsonify(rooms.split(',')) if rooms is not None else []

    @app.route('/rooms', methods=['PUT'])
    def create_new_room():
        try:
            room_number = request.form['room_number']
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT OR IGNORE INTO room VALUES (?)', (room_number,))
                conn.commit()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return get_all_rooms()

    @app.route('/rooms/<room_number>', methods=['DELETE'])
    def delete_room(room_number):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM active_device WHERE room_number = ?', (room_number,))
                cursor.execute(
                    'DELETE FROM room WHERE room_number = ?', (room_number,))
                conn.commit()
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return get_all_rooms()

    @app.route('/rooms/<room_number>', methods=['GET'])
    def get_room_details(room_number):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT room_number, group_concat(mac_address), group_concat(state) FROM room NATURAL LEFT OUTER JOIN active_device NATURAL LEFT OUTER JOIN customer_state WHERE room_number = ?', (room_number,))
                room_number, mac_addresses, states = cursor.fetchone()
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            if room_number is None:
                abort(404)
            return jsonify({
                'room_number': room_number,
                'devices': list(zip(mac_addresses.split(','), states.split(','))) if mac_addresses is not None else []
            })

    @app.route('/rooms/<room_number>/devices', methods=['PUT'])
    def connect_device_to_a_room(room_number):
        try:
            mac_address = request.form['mac_address']
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO active_device VALUES (?, ?)',
                               (room_number, mac_address,))
                cursor.execute('INSERT OR IGNORE INTO customer_state VALUES (?, ?)',
                               (mac_address, 'CHECKED_IN',))
                conn.commit()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return get_room_details(room_number)

    @app.route('/rooms/<room_number>/devices', methods=['DELETE'])
    def disconnect_all_devices_from_a_room(room_number):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM active_device WHERE room_number = ?', (room_number,))
                conn.commit()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return get_room_details(room_number)

    @app.route('/rooms/<room_number>/devices/<mac_address>', methods=['DELETE'])
    def disconnect_device_from_a_room(room_number, mac_address):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM active_device WHERE room_number = ? AND mac_address = ?', (room_number, mac_address,))
                conn.commit()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return get_room_details(room_number)

    @app.route('/devices/<mac_address>', methods=['GET'])
    def get_device_details(mac_address):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT mac_address, state, group_concat(room_number) FROM active_device NATURAL JOIN customer_state WHERE mac_address = ?', (mac_address,))
                mac_address, state, room_numbers = cursor.fetchone()
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            if mac_address is None:
                abort(404)
            return jsonify({
                'mac_address': mac_address,
                'state': state,
                'room_numbers': room_numbers.split(',')
            })

    @app.route('/devices/<mac_address>', methods=['PUT'])
    def update_customer_state(mac_address):
        try:
            state = request.form['state']
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE customer_state SET state = ? WHERE mac_address = ?', (state, mac_address,))
                conn.commit()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return get_device_details(mac_address)

    @app.route('/devices/<mac_address>', methods=['DELETE'])
    def disable_device(mac_address):
        try:
            with create_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM active_device WHERE mac_address = ?', (mac_address,))
                cursor.execute(
                    'DELETE FROM customer_state WHERE mac_address = ?', (mac_address,))
                conn.commit()
        except KeyError:
            abort(400)
        except:
            print("Unexpected error:", sys.exc_info())
            abort(500)
        else:
            return str(cursor.rowcount)

    @app.route('/admin', methods=['GET'])
    def get_admin_page():
        return send_from_directory('static', 'admin.html')

    return app
