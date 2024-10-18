window.addEventListener('beforeunload', function(event) {
    // Reemplaza la URL actual sin reenvío de datos
    window.location.replace(window.location.href);
});


document.getElementById("toggleBtn").onclick = function() {
    var sidebar = document.getElementById("sidebar");
    if (sidebar.style.left === "-250px") {
        sidebar.style.left = "0";
    } else {
        sidebar.style.left = "-250px";
    }
};
