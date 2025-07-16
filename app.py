from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)  # Permitir CORS para conectar con GitHub Pages

# Datos mock (luego se conectará a SharePoint)
tareas = [
    {"ID": "1", "Título": "Revisión de KPIs"},
    {"ID": "2", "Título": "Actualizar dashboard"},
    {"ID": "3", "Título": "Reunión con equipo CX"}
]

@app.route("/tareas", methods=["GET"])
def get_tareas():
    return jsonify(tareas)

@app.route("/comentarios", methods=["POST"])
def save_comentario():
    data = request.get_json()
    data["fecha"] = datetime.datetime.now().isoformat()
    print("Comentario recibido:", data)
    return jsonify({"status": "ok", "data": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
