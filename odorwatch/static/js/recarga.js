document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('myForm');
    const formSubmittedKey = 'formSubmitted';

    // Verificar si el formulario ya ha sido enviado
    if (localStorage.getItem(formSubmittedKey)) {
        console.log('Formulario ya enviado, evitando reenvío.');
        // Aquí puedes mostrar un mensaje o redirigir al usuario
        return;
    }

    form.addEventListener('submit', function(event) {
        // Guardar el estado de envío en el almacenamiento local
        localStorage.setItem(formSubmittedKey, 'true');
    });

    // Opcional: Limpiar el estado al cerrar la página o después de un tiempo
    window.addEventListener('beforeunload', function() {
        localStorage.removeItem(formSubmittedKey);
    });
});
