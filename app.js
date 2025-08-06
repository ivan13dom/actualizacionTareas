// Cargar tareas al cargar la página
document.addEventListener("DOMContentLoaded", () => {
  fetch("https://actualizaciontareas.onrender.com/tareas")
    .then(response => response.json())
    .then(data => {
      const select = document.getElementById("tareas");
      select.innerHTML = ""; // Limpiar opciones anteriores

      if (data.length === 0) {
        const option = document.createElement("option");
        option.text = "No hay tareas disponibles";
        select.add(option);
        return;
      }

      data.forEach(tarea => {
        const option = document.createElement("option");
        option.value = tarea.ID;
        option.text = tarea.Título;
        select.appendChild(option);
      });
    })
    .catch(error => {
      console.error("Error al cargar tareas:", error);
      const select = document.getElementById("tareas");
      select.innerHTML = '<option>Error al cargar tareas</option>';
    });
});

// Guardar comentario
function guardarComentario() {
  const tarea = document.getElementById("tareas").value;
  const comentario = document.getElementById("comentario").value;

  if (!tarea || !comentario) {
    alert("Por favor completá todos los campos.");
    return;
  }

  // Mostrar overlay de carga
  document.getElementById("loadingOverlay").style.display = "flex";

  fetch("https://actualizaciontareas.onrender.com/comentarios", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ id: tarea, comentario: comentario })
  })
    .then(response => response.json())
    .then(data => {
      alert("✅ Actualización guardada correctamente.");
      document.getElementById("comentario").value = "";
    })
    .catch(error => {
      console.error("Error al guardar el comentario:", error);
      alert("⚠️ Ocurrió un error al guardar la actualización.");
    })
    .finally(() => {
      // Ocultar overlay
      document.getElementById("loadingOverlay").style.display = "none";
    });
}
