document.addEventListener('DOMContentLoaded', function() {
    const urls = ['snifa', '#'];  // Asegúrate de que esta lista se actualice dinámicamente si es necesario
    const container = document.getElementById('urls');

    // Construir el HTML de la lista
    let listHTML = ``;
    urls.forEach(url => {
        let iconClass = '';
        let cardTitle = '';
        let cardText = '';

        if (url === 'snifa') {
            iconClass = 'fa-leaf';
            cardTitle = 'SNIFA';
            cardText = 'Accede al módulo SNIFA para más información.';
        } else if (url === '#') {
            iconClass = 'fa-stopwatch';
            cardTitle = 'Enlace no disponible';
            cardText = 'Este enlace no está disponible actualmente.';
        } else {
            iconClass = 'fa-question';
            cardTitle = 'Desconocido';
            cardText = 'Información no disponible.';
        }

        listHTML += `
            <div class="card">
                <div class="card-wrapper">
                    <div class="card-icon">
                        <div class="icon-cart-box">
                            <i class="fa-solid ${iconClass}"></i>
                        </div>
                    </div>
                    <div class="card-content">
                        <div class="card-title-wrapper">
                            <span class="card-title">${cardTitle}</span>
                            <span class="card-action">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    height="15"
                                    width="15"
                                    viewBox="0 0 384 512">
                                </svg>
                            </span>
                        </div>
                        <div class="card-text">
                            ${cardText}
                        </div>
                        ${url !== '#' ? `<a href="/${url}/"><button type="button" class="btn-accept">${url}</button></a>` : '<span class="disabled">Enlace no disponible</span>'}
                    </div>
                </div>
            </div>`;
    });
    listHTML += ``;

    // Insertar el HTML en el contenedor
    container.innerHTML = listHTML;
});
