import os
import libsql_client
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Permitimos CORS para que la página del tarjetón pueda enviar los datos sin bloqueos
CORS(app)

# Conexión protegida mediante variables de entorno
TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

# Inicializamos el cliente oficial de Turso
db = libsql_client.create_client(url=TURSO_URL, authToken=TURSO_TOKEN)

@app.route('/registrar-voto', methods=['POST'])
def registrar_voto():
    data = request.get_json()
    if not data or 'hash' not in data:
        return jsonify({"status": "error", "message": "Falta el hash del voto"}), 400
    
    voto_hash = data['hash']

    try:
        # Insertamos el hash en la tabla de Turso que acabas de crear
        db.execute(
            "INSERT INTO votos_presidenciales (voto_hash) VALUES (?)",
            [voto_hash]
        )
        return jsonify({"status": "success", "message": "Voto encriptado y registrado"}), 200
    except Exception as e:
        # Captura si el hash ya existe (voto duplicado malicioso) u otro error
        return jsonify({"status": "error", "message": "El voto no pudo ser procesado o ya fue registrado"}), 500

if __name__ == '__main__':
    # Railway asigna el puerto automáticamente mediante la variable PORT
    puerto = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=puerto)
  
