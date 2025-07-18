const API_BASE = "https://actualizaciontareas.onrender.com"; // Cambia por la URL de tu backend en Render

// Cargar tareas desde el backend
async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE}/tareas`);
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
        const tasks = await response.json();

        const dropdown = document.getElementById("taskDropdown");
        dropdown.innerHTML = ""; // Limpiar opciones

        if (tasks.length === 0) {
            const option = document.createElement("option");
            option.textContent = "No hay tareas disponibles";
            option.disabled = true;
            dropdown.appendChild(option);
            return;
        }

        tasks.forEach(task => {
            const option = document.createElement("option");
            option.value = task.ID;
            option.textContent = task["Título"]; // Campo exacto
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error("Error cargando tareas:", error);
        showMessage("Error al cargar las tareas", "danger");
    }
}

// Guardar actualización
async function saveUpdate() {
    const taskId = document.getElementById("taskDropdown").value;
    const comment = document.getElementById("commentInput").value;

    if (!taskId || !comment.trim()) {
        showMessage("Selecciona una tarea y escribe un comentario", "danger");
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/comentarios`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ID: taskId,
                comentario: comment,
                fecha: new Date().toISOString()
            })
        });

        if (response.ok) {
            showMessage("✅ Actualización guardada correctamente", "success");
            document.getElementById("commentInput").value = "";
        } else {
            showMessage("Error al guardar la actualización", "danger");
        }
    } catch (error) {
        console.error("Error guardando comentario:", error);
        showMessage("Error al guardar la actualización", "danger");
    }
}

// Mostrar mensajes
function showMessage(msg, type) {
    const messageDiv = document.getElementById("message");
    messageDiv.className = `mt-3 alert alert-${type}`;
    messageDiv.textContent = msg;
}

// Eventos
document.getElementById("submitBtn").addEventListener("click", saveUpdate);
document.addEventListener("DOMContentLoaded", loadTasks);
