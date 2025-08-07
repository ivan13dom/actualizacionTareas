from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import datetime
import subprocess
import requests
import logging

app = Flask(__name__)
CORS(app)

# Logging detallado
logging.basicConfig(level=logging.DEBUG)

# Variables en memoria (se reinician si Render reinicia)
tareas_data = []
actualizaciones_data = []

# Configuración del repositorio
GITHUB_REPO = "ivan13dom/actualizacionTareas"
TAREAS_FILE = "tareas.json"
ACTUALIZACIONES_FILE = "actualizaciones.json"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# ==============================
# Función para hacer commit seguro a GitHub
# ==============================
def commit_to_github(filename, content):
    try:
        repo_path = "."

        # Inicializar si no existe .git
        if not os.path.isdir(os.path.join(repo_path, ".git")):
            subprocess.run(["git", "init"], cwd=repo_path, check=True)
            subprocess.run(["git", "checkout", "-b", "main"], cwd=repo_path, check=True)
            subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{GITHUB_REPO}.git"], cwd=repo_path, check=True)

        # Configurar usuario
        subprocess.run(["git", "config", "--global", "user.email", "bot@render.com"])
        subprocess.run(["git", "config", "--global", "user.name", "Render Bot"])

        # Actualizar desde GitHub
        subprocess.run(["git", "fetch", "origin"], cwd=repo_path, check=True)
        subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True)
        subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=repo_path, check=True)

        # Guardar contenido
        with open(os.path.join(repo_path, filename), "w") as f:
            json.dump(content, f, indent=4)

        subprocess.run(["git", "add", filename], cwd=repo_path, check=True)

        result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True)
        if not result.stdout.strip():
            app.logger.info(f"[INFO] No hay cambios en {filename}.")
            return

        subprocess.run(["git", "commit", "-m", f"Update {filename}"], cwd=repo_path, check=True)

        # Push con token directamente embebido
        push_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
        subprocess.run(["git", "push", push_url, "main"], cwd=repo_path, check=True)

    except subprocess.CalledProcessError as e:
        app.logger.error(f"[ERROR] Git push fallido: {e}")



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

        # Obtener actualizaciones existentes desde GitHub
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{ACTUALIZACIONES_FILE}"
        response = requests.get(raw_url)

        if response.status_code == 200:
            try:
                actualizaciones = response.json()
            except json.JSONDecodeError:
                actualizaciones = []
        else:
            actualizaciones = []

        actualizaciones.append(data)

        commit_to_github(ACTUALIZACIONES_FILE, actualizaciones)

        return jsonify({"status": "ok", "message": "Comentario guardado"})
    except Exception as e:
        app.logger.error(f"Error en save_comentario: {e}")
        return jsonify({"error": str(e)}), 500


# ==============================
# Run
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
