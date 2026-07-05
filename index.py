import os
from flask import Flask, request, jsonify
from flask_cors import CORS
# LA SOLUCIÓN AL ERROR DE ATRIBUTO: Importamos el cliente síncrono oficial
from libsql_client import create_client_sync

app = Flask(__name__)
CORS(app)

# Conexión protegida mediante variables de entorno
TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

# Inicializamos el cliente de forma correcta y compatible
db = create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN)

# SOLUCIÓN AL "FAILED TO RESPOND": Agregamos una respuesta para la página principal
@app.route('/', methods=['GET'])
def inicio():
    return jsonify({"status": "online", "message": "Servidor de votación de Celania activo"}), 200

@app.route('/registrar-voto', methods=['POST'])
def registrar_voto():
    data = request.get_json()
    if not data or 'hash' not in data:
        return jsonify({"status": "error", "message": "Falta el hash del voto"}), 400
    
    voto_hash = data['hash']

    try:
        # Insertamos el hash en la tabla de Turso
        db.execute(
            "INSERT INTO votos_presidenciales (voto_hash) VALUES (?)",
            [voto_hash]
        )
        return jsonify({"status": "success", "message": "Voto encriptado y registrado"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "El voto no pudo ser procesado o ya fue registrado"}), 500

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=puerto)
    
