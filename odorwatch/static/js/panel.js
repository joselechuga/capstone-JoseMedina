document.getElementById('runScriptBtn').addEventListener('click', function () {
    // Iniciar la barra de progreso
    updateProgressBar(0);

    // Hacer la solicitud AJAX
    fetch("{% url 'run_script' %}")
    .then((response) => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then((data) => {
        if (data.output) {
            console.log('Ejecutado correctamente');
            updateProgressBar(100); // Completa la barra de progreso al finalizar
        } else if (data.error) {
            console.log('ERROR: ', data.error);
        }
    })
    .catch((error) => {
        console.error('Error al ejecutar el script:', error);
        // Aquí puedes manejar el error de manera más específica
    });
});

function updateProgressBar(percentage) {
    const progressBar = document.getElementById('progress-bar2');
    progressBar.style.width = percentage + '%';
    progressBar.setAttribute('aria-valuenow', percentage);
    progressBar.textContent = percentage + '%'; // Mostrar el porcentaje en la barra
}

function fetchLogs() {
    fetch('/get-logs/')
        .then((response) => response.json())
        .then((data) => {
            const logOutput = document.getElementById('log-output');
            const isScrolledToBottom = logOutput.scrollHeight - logOutput.clientHeight <= logOutput.scrollTop + 1;
            if (data.logs) {
                logOutput.innerHTML = ''; // Usar innerHTML para limpiar el contenido
                const last100Logs = data.logs.slice(-100); // filas a mostrar de logs
                last100Logs.forEach((log) => {
                    // Eliminar los milisegundos y el texto " - INFO - " de cada log
                    const cleanedLog = log.replace(/,\d{3}/, '').replace(/ - INFO - /g, '');
                    // Añadir un espacio después de los datos numéricos de tiempo
                    const formattedLog = cleanedLog.replace(/(\d{2}:\d{2}:\d{2})(\S)/, '$1 $2');
                    const logParagraph = `<p class="texto-logs"><span class="log-decorator">></span> ${formattedLog}</p>`; // Usar plantilla de cadena
                    logOutput.innerHTML += logParagraph; // Usar innerHTML para añadir el contenido
                });
                if (isScrolledToBottom) {
                    logOutput.scrollTop = logOutput.scrollHeight;
                }
            } else if (data.error) {
                logOutput.innerHTML = 'Error: ' + data.error; // Usar innerHTML para mostrar el error
                console.error('Error al leer el archivo:', data.error);
            }
        })
        .catch((error) => {
            const errorMessage = 'Error al obtener los logs: ' + error;
            document.getElementById('log-output').innerHTML = errorMessage; // Usar innerHTML para mostrar el error
            console.error(errorMessage);
        });
}

fetchLogs();
setInterval(fetchLogs, 2000);

function checkProgress() {
fetch('/get-progress/')
    .then((response) => response.json())
    .then((data) => {
    if (data.progress !== undefined) {
        updateProgressBar(data.progress);
    }
    })
    .catch((error) => console.error('Error al obtener el progreso:', error));
}

// Llama a checkProgress periódicamente
setInterval(checkProgress, 1000);