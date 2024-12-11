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

document.addEventListener('DOMContentLoaded', function() {
    // Código existente...
    
    // Funcionalidad para desmarcar un checkbox cuando se marca el otro
    function toggleCheckboxes(superuserCheckbox, notSuperuserCheckbox) {
        superuserCheckbox.addEventListener('change', function() {
            if (this.checked) {
                notSuperuserCheckbox.checked = false;
            }
        });

        notSuperuserCheckbox.addEventListener('change', function() {
            if (this.checked) {
                superuserCheckbox.checked = false;
            }
        });
    }

    // Aplicar la funcionalidad a los formularios de edición
    document.querySelectorAll('.modal').forEach(function(modal) {
        modal.addEventListener('show.bs.modal', function(event) {
            var modalId = event.target.id.replace('editModal', '');
            var isSuperuserCheckbox = document.getElementById('is_superuser_' + modalId);
            var isNotSuperuserCheckbox = document.getElementById('is_not_superuser_' + modalId);

            toggleCheckboxes(isSuperuserCheckbox, isNotSuperuserCheckbox);
        });
    });

    // Aplicar la funcionalidad al formulario de creación
    var createSuperuserCheckbox = document.getElementById('is_superuser');
    var createNotSuperuserCheckbox = document.getElementById('is_not_superuser');

    if (createSuperuserCheckbox && createNotSuperuserCheckbox) {
        toggleCheckboxes(createSuperuserCheckbox, createNotSuperuserCheckbox);
    }
});

