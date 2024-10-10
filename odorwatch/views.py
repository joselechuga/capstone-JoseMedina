import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

def custom_404(request, exception):
    return render(request, '404.html',{})


def buscar_usuario_por_correo(correo):
    try:
        usuario = User.objects.get(email=correo)
        return usuario
    except User.DoesNotExist:
        return None

def index(request):
    try:
        return render(request, 'index.html')
    
    except Exception as e:
        return render(request, 'error.html', {'error_message': str(e)})

def home(request):
    try:
        return render(request, 'home.html')
    
    except Exception as e:
        return render(request, 'error.html', {'error_message': str(e)})

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
            validar = buscar_usuario_por_correo(correo)
            
            if validar is not None:
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