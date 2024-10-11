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
    email = None
    m365_email = None
    
    if request.user.is_authenticated:
        email = request.user.email
        # Suponiendo que tienes una forma de obtener el correo de M365
        if '@tsgenviro.com' in email:
            m365_email = email
    
    return render(request, 'home.html', {'email': email, 'm365_email': m365_email})
# Login para verificar el acceso a panel
@csrf_exempt
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'home.html')
        elif 'correo' in request.POST and 'firma' in request.POST and 'certificado' in request.POST:
            correo = request.POST.get('correo')
            firma = request.POST.get('firma')
            certificado = request.POST.get('certificado')
            
            # Aquí deberías implementar la lógica de validación para estas variables
            # Por ejemplo:
            user = authenticate(request, username='jose', password='Capstonejose')
            if user is not None:
                login(request, user)
                return render(request, 'home.html')
            else:
                return render(request, 'login.html', {'error_message': 'Credenciales incorrectas'})
        else:
            return render(request, 'login.html', {'error_message': 'Credenciales incorrectas o falta información'})

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