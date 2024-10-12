import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from django.views.decorators.csrf import csrf_exempt

def custom_404(request, exception):
    return render(request, '404.html',{})


def index(request):
    try:
        return render(request, 'index.html')
    
    except Exception as e:
        return render(request, 'error.html', {'error_message': str(e)})

def home(request):
    if request.method == 'POST':
        # Obtener los datos enviados por el formulario
        correo = request.POST.get('correo')
        certificado = request.POST.get('certificado')
        firma = request.POST.get('firma')

        # Pasar los datos al template
        return render(request, 'home.html', {
            'correo': correo,
            'certificado': certificado,
            'firma': firma,
        })
    else:
        return render(request, 'home.html')

# Login para verificar el acceso a panel
@csrf_exempt
def loginPage(request):
    if request.method == 'POST':
        # Extraer los valores del 'Payload'
        correo = request.POST.get('correo')
        firma = request.POST.get('firma')
        certificado = request.POST.get('certificado')

        # Validar si el correo, firma y certificado existen
        if correo and firma and certificado:
            # Guardar los valores en la sesión
            request.session['correo'] = correo
            request.session['firma'] = firma
            request.session['certificado'] = certificado

            # Autenticar al usuario
            user = authenticate(request, username='jose', password='Capstonejose')
            if user is not None:
                login(request, user)
                return render(request, 'home.html')
            else:
                return render(request, 'login.html', {'error_message': 'Credenciales incorrectas'})
        else:
            return render(request, 'login.html', {'error_message': 'Faltan datos en el formulario'})

    return render(request, 'login.html')



@login_required(login_url='/login/')
def panel(request):
    try:
        return render(request, 'index.html')
    except Exception as e:
        return render(request, 'error.html', {'error_message': str(e)})

# Cerrar sesion
def logoutUser(request):
    logout(request)
    return redirect('login')