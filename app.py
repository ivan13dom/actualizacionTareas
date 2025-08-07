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
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        # Paso 1: Obtener el SHA actual del archivo (si existe)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            sha = response.json()["sha"]
        else:
            sha = None  # Archivo nuevo

        # Paso 2: Preparar nuevo contenido (base64)
        import base64
        new_content = json.dumps(content, indent=4)
        b64_content = base64.b64encode(new_content.encode()).decode()

        # Paso 3: Hacer PUT con el nuevo contenido
        payload = {
            "message": f"Update {filename}",
            "content": b64_content,
            "branch": "main"
        }

        if sha:
            payload["sha"] = sha  # Requerido para modificar

        put_response = requests.put(url, headers=headers, json=payload)

        if put_response.status_code in [200, 201]:
            app.logger.info(f"[INFO] {filename} actualizado correctamente en GitHub.")
        else:
            app.logger.error(f"[ERROR] Falló el update en GitHub: {put_response.status_code} - {put_response.text}")

    except Exception as e:
        app.logger.error(f"[ERROR] commit_to_github(): {e}")


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
