window.addEventListener('beforeunload', function (event) {
    // Reemplaza la URL actual sin reenvío de datos
    window.location.replace(window.location.href);
});


document.getElementById("toggleBtn").onclick = function () {
    var sidebar = document.getElementById("sidebar");
    if (sidebar.style.left === "-250px") {
        sidebar.style.left = "0";
    } else {
        sidebar.style.left = "-250px";
    }
};


  // Función para mostrar/ocultar sublistas específicas
  function toggleSublista(id) {
    const sublista = document.getElementById(id);
    if (sublista.style.display === "none" || sublista.style.display === "") {
      sublista.style.display = "block"; // Muestra la sublista
    } else {
      sublista.style.display = "none"; // Oculta la sublista
    }
  }