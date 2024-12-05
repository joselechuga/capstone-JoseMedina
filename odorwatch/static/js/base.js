document.addEventListener("DOMContentLoaded", function(event) {
    const showNavbar = (toggleId, navId, bodyId, headerId) =>{
    const toggle = document.getElementById(toggleId),
    nav = document.getElementById(navId),
    bodypd = document.getElementById(bodyId),
    headerpd = document.getElementById(headerId)
    
    // Validar que todas las variables existan
    if(toggle && nav && bodypd && headerpd){
    // Mostrar la barra de navegación inicialmente
    nav.classList.add('show')
    // Cambiar icono
    toggle.classList.add('bx-x')
    // Añadir padding al cuerpo
    bodypd.classList.add('body-pd')
    // Añadir padding al encabezado
    headerpd.classList.add('body-pd')

    toggle.addEventListener('click', ()=>{
    // Alternar la visibilidad de la barra de navegación
    nav.classList.toggle('show')
    // Alternar el icono
    toggle.classList.toggle('bx-x')
    // Alternar el padding del cuerpo
    bodypd.classList.toggle('body-pd')
    // Alternar el padding del encabezado
    headerpd.classList.toggle('body-pd')
    })
    }
}

showNavbar('header-toggle','nav-bar','body-pd','header')

/*===== LINK ACTIVE =====*/
const linkColor = document.querySelectorAll('.nav_link')

function colorLink(){
if(linkColor){
linkColor.forEach(l=> l.classList.remove('active'))
this.classList.add('active')
}
}
linkColor.forEach(l=> l.addEventListener('click', colorLink))

    // Tu código para ejecutar una vez que el DOM esté cargado y listo
});