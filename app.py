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

# ==============================
# Función para hacer commit seguro en GitHub
# ==============================
def commit_to_github(filename, content):
    repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    repo_path = "."

    subprocess.run(["git", "config", "--global", "user.email", "bot@render.com"])
    subprocess.run(["git", "config", "--global", "user.name", "Render Bot"])

    # Sincronizar con remoto antes de commit
    subprocess.run(["git", "-C", repo_path, "fetch", repo_url])
    subprocess.run(["git", "-C", repo_path, "reset", "--hard", "FETCH_HEAD"])

    # Guardar archivo actualizado
    with open(filename, "w") as f:
        json.dump(content, f, indent=4)

    # Commit y push
    subprocess.run(["git", "-C", repo_path, "add", filename])
    subprocess.run(["git", "-C", repo_path, "commit", "-m", f"Update {filename}"])
    subprocess.run(["git", "-C", repo_path, "push", repo_url, "HEAD:main"])

# ==============================
# Endpoint: Obtener tareas
# ==============================
@app.route("/tareas", methods=["GET"])
def get_tareas():
    return jsonify(tareas_data)

# ==============================
# Endpoint: Sincronizar tareas (desde Power Automate)
# ==============================
@app.route("/sync-tareas", methods=["POST"])
def sync_tareas():
    global tareas_data
    try:
        raw_data = request.data.decode("utf-8")
        app.logger.debug(f"Body recibido: {raw_data[:200]}...")
        tareas = json.loads(raw_data)
        tareas_data = tareas

        # Subir backup a GitHub
        commit_to_github(TAREAS_FILE, tareas)

        return jsonify({"status": "ok", "message": "Tareas actualizadas"})
    except Exception as e:
        app.logger.error(f"Error en sync_tareas: {e}")
        return jsonify({"error": str(e)}), 500

# ==============================
# Endpoint: Guardar comentario
# ==============================
@app.route("/comentarios", methods=["POST"])
def save_comentario():
    try:
        data = request.get_json()
        data["fecha"] = datetime.datetime.now().isoformat()

        # Leer actualizaciones existentes desde GitHub RAW
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{ACTUALIZACIONES_FILE}"
        response = requests.get(raw_url)

        if response.status_code == 200:
            try:
                actualizaciones = response.json()
            except json.JSONDecodeError:
                actualizaciones = []
        else:
            actualizaciones = []

        # Agregar nuevo comentario
        actualizaciones.append(data)

        # Subir actualizaciones actualizadas a GitHub
        commit_to_github(ACTUALIZACIONES_FILE, actualizaciones)

        return jsonify({"status": "ok", "message": "Comentario guardado"})
    except Exception as e:
        app.logger.error(f"Error en save_comentario: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)