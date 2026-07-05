import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Configuración global abierta para producción sin restricciones de dominio
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if TURSO_URL and TURSO_URL.startswith("libsql://"):
    TURSO_HTTP_URL = TURSO_URL.replace("libsql://", "https://") + "/v1/execute"
else:
    TURSO_HTTP_URL = TURSO_URL

@app.route('/', methods=['GET'])
def inicio():
    return jsonify({"status": "online", "message": "Servidor de votación de Celania activo"}), 200

@app.route('/registrar-voto', methods=['POST', 'OPTIONS'], strict_slashes=False)
def registrar_voto():
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200

    if not TURSO_HTTP_URL or not TURSO_TOKEN:
        return jsonify({"status": "error", "message": "Faltan las credenciales de la base de datos en Railway"}), 500

    # Volvemos a la recepción estándar por JSON
    data = request.get_json()
    if not data or 'hash' not in data:
        return jsonify({"status": "error", "message": "Falta el hash del voto"}), 400
    
    voto_hash = data['hash']

    headers = {
        "Authorization": f"Bearer {TURSO_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "statements": [
            {
                "q": "INSERT INTO votos_presidenciales (voto_hash) VALUES (?);",
                "params": [voto_hash]
            }
        ]
    }

    try:
        response = requests.post(TURSO_HTTP_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Voto encriptado y registrado"}), 200
        else:
            return jsonify({"status": "error", "message": "El voto ya fue registrado anteriormente"}), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error interno: {str(e)}"}), 500

@app.errorhandler(405)
def metodo_no_permitido(e):
    return jsonify({"status": "error", "message": "Método no permitido"}), 405

@app.errorhandler(404)
def ruta_no_encontrada(e):
    return jsonify({"status": "error", "message": "Ruta no encontrada"}), 404
    
