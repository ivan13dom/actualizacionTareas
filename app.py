from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import datetime
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
CORS(app)

# Variables en memoria (se reinician si Render reinicia)
tareas_data = []
actualizaciones_data = []

# Datos para GitHub
GITHUB_REPO = "ivan13dom/actualizacionTareas"  # Ej: ivan13dom/actualizaciones-tareas
TAREAS_FILE = "tareas.json"
ACTUALIZACIONES_FILE = "actualizaciones.json"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Definido en Render

# Función para hacer commit a GitHub
def commit_to_github(filename, content):
    with open(filename, "w") as f:
        json.dump(content, f, indent=4)

    repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    repo_path = "."

    subprocess.run(["git", "config", "--global", "user.email", "bot@render.com"])
    subprocess.run(["git", "config", "--global", "user.name", "Render Bot"])

    # Traer cambios antes de hacer commit
    subprocess.run(["git", "-C", repo_path, "pull", repo_url, "main", "--rebase"])

    subprocess.run(["git", "-C", repo_path, "add", filename])
    subprocess.run(["git", "-C", repo_path, "commit", "-m", f"Update {filename}"])
    subprocess.run(["git", "-C", repo_path, "push", repo_url, "HEAD:main"])


# 1. Obtener lista de tareas
@app.route("/tareas", methods=["GET"])
def get_tareas():
    return jsonify(tareas_data)

# 2. Sincronizar tareas (desde Power Automate)
@app.route("/sync-tareas", methods=["POST"])
def sync_tareas():
    global tareas_data
    try:
        raw_data = request.data.decode("utf-8")  # Lee el body como texto
        app.logger.debug(f"Body recibido: {raw_data[:200]}")  # Log de debug (primeros 200 caracteres)
        
        try:
            tareas = json.loads(raw_data)  # Convertir a JSON
        except json.JSONDecodeError as e:
            app.logger.error(f"Error parseando JSON: {e}")
            return jsonify({"error": "JSON inválido"}), 400

        tareas_data = tareas
        # commit_to_github(TAREAS_FILE, tareas)  # Lo dejamos comentado por ahora para testear
        return jsonify({"status": "ok", "message": "Tareas actualizadas"})
    except Exception as e:
        app.logger.error(f"Error en sync_tareas: {e}")
        return jsonify({"error": str(e)}), 500


# 3. Guardar comentario
@app.route("/comentarios", methods=["POST"])
def save_comentario():
    global actualizaciones_data
    try:
        data = request.get_json()
        data["fecha"] = datetime.datetime.now().isoformat()
        actualizaciones_data.append(data)

        # Subir actualizaciones a GitHub
        commit_to_github(ACTUALIZACIONES_FILE, actualizaciones_data)

        return jsonify({"status": "ok", "message": "Comentario guardado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
