import json
import os
from flask import Flask, jsonify, request, session, Response
import psycopg2
import psycopg2.extras

with open("config.json", "r", encoding="utf-8") as json_file:
    config_data = json.load(json_file)

conn = psycopg2.connect("dbname={} user={} password={} host={}".format(config_data["db_name"], config_data["db_user"], config_data["db_password"], config_data["db_host"]))

cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

app = Flask(__name__)

app.secret_key = config_data["secret_key"]

@app.route('/')
def home():
    Response.headers.add("Access-Control-Allow-Origin", "*")
    if 'userId' in session:
        return jsonify({"name": "Dona Benta API", "version": "1.0.0", "session": session["userId"]})
    else:
        return jsonify({"name": "Dona Benta API", "version": "1.0.0"})

@app.route('/login', methods=["POST", "GET"])
def login():
    
    Response.headers.add("Access-Control-Allow-Origin", "*")
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

        cursor.close()
        
        if login_is_right:
            return jsonify({"status": True}), 200
            
        else: 
            return jsonify({"status": False}), 401

@app.route('/logout', methods=["POST"])
def logout():
    
    Response.headers.add("Access-Control-Allow-Origin", "*")
    session.pop("userId", None)
    return jsonify({"status": "ok"})

@app.route('/signup', methods=["POST"])
def signup():
    
    Response.headers.add("Access-Control-Allow-Origin", "*")
    if request.method == "POST":
        
        signup_data = request.get_json()

        signup_query = f'''INSERT INTO public."Usuario"("Nome", "Senha", "Email") VALUES ('{signup_data['name']}', '{signup_data['password']}', '{signup_data['email']}');''' 

        cursor.execute(signup_query)
        conn.commit()
        cursor.close()

        return jsonify({"status": True}), 200

@app.route('/dispositivoLogin', methods=["POST"])
def dispositivoLogin():
    
    Response.headers.add("Access-Control-Allow-Origin", "*")
    dispositivo_session = request.get_json()
    session["key_dispositivo"] = dispositivo_session["key"]
    return jsonify({"message": session["key_dispositivo"]})

@app.route('/dispositivoLogout', methods=["POST"])
def dispositivoLogout():
    
    Response.headers.add("Access-Control-Allow-Origin", "*")
    session.pop("key_dispositivo", None)
    return jsonify({"message": "ok"})

@app.route('/status', methods=["GET"])
def status():
    
    Response.headers.add("Access-Control-Allow-Origin", "*")
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
