import json
import os
from flask import Flask, jsonify, request, session
from flask_cors import CORS
import psycopg2
import psycopg2.extras

with open("config.json", "r", encoding="utf-8") as json_file:
    config_data = json.load(json_file)

conn = psycopg2.connect("dbname={} user={} password={} host={}".format(config_data["db_name"], config_data["db_user"], config_data["db_password"], config_data["db_host"]))

cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

app = Flask(__name__)
CORS(app)
app.secret_key = config_data["secret_key"]

@app.route('/')
def home():
    if 'userId' in session:
        return jsonify({"name": "Dona Benta API", "version": "1.0.0", "session": session["userId"]})
    else:
        return jsonify({"name": "Dona Benta API", "version": "1.0.0"})

@app.route('/login', methods=["POST", "GET"])
def login():
        
    if request.method == "POST":    
        
        userQuery = '''SELECT "IdUsuario", "Nome", "Senha", "Email" FROM public."Usuario";'''
        cursor.execute(userQuery)
        login_is_right = False

        results = cursor.fetchall()
        
        login_data_from_user = request.get_json()
        
        for row in results:
            login_is_right = login_data_from_user["email"] == row["Email"] and login_data_from_user["password"] == row["Senha"]
            if login_is_right:
                session["userId"] = row["IdUsuario"]

        
        if login_is_right:
            return jsonify({session: session["userId"]}), 200
            
        else: 
            return jsonify({"status": False}), 401

@app.route('/logout', methods=["POST"])
def logout():
    session.pop("userId", None)
    return jsonify({"status": "ok"})

@app.route('/signup', methods=["POST"])
def signup():
    if request.method == "POST":
        
        signup_data = request.get_json()

        signup_query = f'''INSERT INTO public."Usuario"("Nome", "Senha", "Email") VALUES ('{signup_data['name']}', '{signup_data['password']}', '{signup_data['email']}');''' 

        cursor.execute(signup_query)
        conn.commit()
        cursor.close()

        return jsonify({"status": True}), 200

@app.route('/dispositivoLogin', methods=["POST"])
def dispositivoLogin():
    dispositivo_session = request.get_json()
    session["key_dispositivo"] = dispositivo_session["key"]
    return jsonify({"message": session["key_dispositivo"]})

@app.route('/dispositivoLogout', methods=["POST"])
def dispositivoLogout():
    session.pop("key_dispositivo", None)
    return jsonify({"message": "ok"})

@app.route('/status', methods=["GET"])
def status():
    print(session["key_dispositivo"])
    if 'key_dispositivo' in session:
        session_query = '''SELECT "IdDispositivo", "Nome", "Status", "IdUsuario"
	FROM public."Dispositivo" WHERE "IdDispositivo" = {};'''.format(session["key_dispositivo"])
        cursor.execute(session_query)
        result = cursor.fetchall()
        
        status = result[0]["Status"]


        conn.commit()
        return jsonify({"status": status})
    else:
        return jsonify({"message": "Sem permissão"}), 401

@app.route('/sendVoiceText', methods=["POST"])
def send_voice_text():
    request_body = request.get_json()
    message = request_body["message"]

    if "ligar" in message:
        query_string = "UPDATE Dispositivo SET Status = true"
        return jsonify({"status": "Ligado!"}), 200
    if "desligar" in message:
        query_string = "UPDATE Dispositivo SET Status = false"
        return jsonify({"status": "Desligado!"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
