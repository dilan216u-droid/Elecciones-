import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Variables de entorno de Railway
TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

# Convertimos la URL de libsql:// a https:// para la API HTTP
if TURSO_URL and TURSO_URL.startswith("libsql://"):
    TURSO_HTTP_URL = TURSO_URL.replace("libsql://", "https://") + "/v1/execute"
else:
    TURSO_HTTP_URL = TURSO_URL

@app.route('/', methods=['GET'])
def inicio():
    return jsonify({"status": "online", "message": "Servidor de votación de Celania activo"}), 200

@app.route('/registrar-voto', methods=['POST'])
def registrar_voto():
    data = request.get_json()
    if not data or 'hash' not in data:
        return jsonify({"status": "error", "message": "Falta el hash del voto"}), 400
    
    voto_hash = data['hash']

    # Estructura de la petición HTTP para Turso
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
        # Enviamos el voto directamente por HTTP
        response = requests.post(TURSO_HTTP_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Voto encriptado y registrado"}), 200
        else:
            return jsonify({"status": "error", "message": "Turso rechazó la consulta o el voto está duplicado"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": "Error de conexión con la base de datos"}), 500

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=puerto)
    
