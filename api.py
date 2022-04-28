import json
import os
from flask import Flask, jsonify, request, session
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
            return jsonify({"status": True}), 200
            
        else: 
            return jsonify({"status": False}), 401

@app.route('/logout', methods=["POST"])
def logout():
    session.pop("userId", None)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
