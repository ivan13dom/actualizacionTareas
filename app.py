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
