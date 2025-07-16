const API_BASE = "https://actualizaciontareas.onrender.com"; // URL del backend en Render

// Cargar tareas desde el backend
async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE}/tareas`);
        const tasks = await response.json(); // Convertir respuesta en JSON

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
            option.textContent = task["Título"]; // Usar la clave exacta
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error("Error cargando tareas:", error);
        showMessage("Error al cargar las tareas", "danger");
    }
}

// Guardar actualización en backend
async function saveUpdate() {
    const taskId = document.getElementById("taskDropdown").value;
    const comment = document.getElementById("commentInput").value;

    if (!taskId || !comment) {
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
            showMessage("Actualización guardada correctamente", "success");
            document.getElementById("commentInput").value = ""; // Limpiar
        } else {
            showMessage("Error al guardar la actualización", "danger");
        }
    } catch (error) {
        console.error("Error guardando comentario:", error);
        showMessage("Error al guardar la actualización", "danger");
    }
}

// Mostrar mensajes al usuario
function showMessage(msg, type) {
    const messageDiv = document.getElementById("message");
    messageDiv.className = `mt-3 alert alert-${type}`;
    messageDiv.textContent = msg;
}

// Inicialización
document.getElementById("submitBtn").addEventListener("click", saveUpdate);
document.addEventListener("DOMContentLoaded", loadTasks);
