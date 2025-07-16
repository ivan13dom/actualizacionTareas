// URL del backend (cuando esté listo en Render)
const API_BASE = "https://actualizaciontareas.onrender.com";

// Cargar tareas (GET /tareas)
async function loadTasks() {
    try {
        // Datos mockeados por ahora
        const tasks = [
            { ID: "1", Titulo: "Revisión de KPIs" },
            { ID: "2", Titulo: "Actualizar dashboard" },
            { ID: "3", Titulo: "Reunión con equipo CX" }
        ];

        const dropdown = document.getElementById("taskDropdown");
        dropdown.innerHTML = ""; // Limpiar opciones
        tasks.forEach(task => {
            const option = document.createElement("option");
            option.value = task.ID;
            option.textContent = task.Titulo;
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error("Error cargando tareas:", error);
    }
}

// Guardar actualización (POST /comentarios)
async function saveUpdate() {
    const taskId = document.getElementById("taskDropdown").value;
    const comment = document.getElementById("commentInput").value;

    if (!taskId || !comment) {
        showMessage("Selecciona una tarea y escribe un comentario", "danger");
        return;
    }

    try {
        // Aquí se enviará al backend real
        // const response = await fetch(`${API_BASE}/comentarios`, {
        //     method: "POST",
        //     headers: { "Content-Type": "application/json" },
        //     body: JSON.stringify({ ID: taskId, comentario: comment, fecha: new Date() })
        // });
        // const data = await response.json();

        // Simulación
        console.log("Datos enviados:", { ID: taskId, comentario: comment });
        showMessage("Actualización guardada correctamente", "success");
        document.getElementById("commentInput").value = ""; // Limpiar
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
