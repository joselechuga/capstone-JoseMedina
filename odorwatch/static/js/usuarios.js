document.getElementById('tabla').addEventListener('click', function() {
    var containerCards = document.getElementById('container-cards-user');
    var tablaUsuarios = document.getElementById('tabla-usuarios');
    var spanTabla = document.getElementById('span-tabla');
    var spanCards = document.getElementById('span-cards');
    
    if (containerCards && tablaUsuarios && spanTabla && spanCards) {
        containerCards.style.display = 'none';
        tablaUsuarios.style.display = 'block';
        spanTabla.style.display = 'inline';
        spanCards.style.display = 'none';
    }
    this.classList.add('active');
    document.getElementById('cards-usuarios').classList.remove('active');
});

document.getElementById('cards-usuarios').addEventListener('click', function() {
    var containerCards = document.getElementById('container-cards-user');
    var tablaUsuarios = document.getElementById('tabla-usuarios');
    var spanTabla = document.getElementById('span-tabla');
    var spanCards = document.getElementById('span-cards');
    
    if (containerCards && tablaUsuarios && spanTabla && spanCards) {
        containerCards.style.display = 'block';
        tablaUsuarios.style.display = 'none';
        spanTabla.style.display = 'none';
        spanCards.style.display = 'inline';
    }
    this.classList.add('active');
    document.getElementById('tabla').classList.remove('active');
});

