import os
import requests
import subprocess
import logging
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from .models import Cliente,UnidadFiscalizable,Documento

def custom_404(request, exception):
    return render(request, '404.html',{})

# Login para verificar el acceso a panel
@csrf_exempt
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Almacenar el correo en la sesión (para usuarios autenticados)
            request.session['user_email'] = user.email
            login(request, user)
            return redirect('home')
        elif 'correo' in request.POST and 'firma' in request.POST and 'certificado' in request.POST:
            correo = request.POST.get('correo')
            firma = request.POST.get('firma')
            certificado = request.POST.get('certificado')
            data = {'user_email': correo, 
                    'firma': firma, 
                    'certificado': certificado
                    }
            # Almacenar el correo en la sesión (para otros usuarios)
            request.session['user_email'] = correo
            
            # Aquí deberías implementar la lógica de validación para estas variables
            user = authenticate(request, username='jose', password='Capstonejose')
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'login.html', {'error_message': 'Credenciales incorrectas'})
        else:
            return render(request, 'login.html', {'error_message': 'Credenciales incorrectas o falta información'})
    
    return render(request, 'login.html')
# Cerrar sesion
def logoutUser(request):
    logout(request)
    return redirect('login')


def home(request):
    # Obtener el correo de la sesión
    user_email = request.session.get('user_email', 'Correo no disponible')    
    return render(request, 'home.html', {'user_email': user_email})


def run_script(request):
    """Ejecuta el script main.py y devuelve la salida."""
    try:
        # Ejecuta el script main.py
        result = subprocess.run(
            ['python', 'modulos\main.py'],
            capture_output=True,
            text=True,
            check=True  #excepción si el script falla
        )
        # Retorna JSON
        return JsonResponse({'output': result.stdout})
    except subprocess.CalledProcessError as e:
        # Captura errores de ejecución del script
        return JsonResponse({'error': f'Error al ejecutar el script: {e.stderr}'})
    except Exception as e:
        # Captura cualquier otro error
        return JsonResponse({'error': f'Error inesperado: {str(e)}'})


@login_required(login_url='/login/')
def panel(request):
    try:
        return render(request, 'panel.html')
    except Exception as e:
        return render(request, 'error.html', {'error_message': str(e)})

# Leer archivo de logs de ejecuciones en scraping
def get_logs(request):
    """Lee el archivo de logs basado en la fecha actual y devuelve su contenido como JSON."""
    try:
        fecha = time.strftime("%Y-%m-%d")
        log_file_path = f"modulos/logs/{fecha}.lst"
        
        # Verifica si el archivo de log existe, si no, lo crea
        if not os.path.exists(log_file_path):
            with open(log_file_path, "w") as log_file:
                log_file.write("")

        with open(log_file_path, "r") as log_file:
            logs = log_file.readlines()
        return JsonResponse({'logs': logs})
    except Exception as e:
        return JsonResponse({'error': f'Error al leer el archivo: {str(e)}'})


def snifa(request):
    clientes = Cliente.objects.all()
    unidades = UnidadFiscalizable.objects.all()
    documentos = Documento.objects.all()
    return render(request, 'snifa.html', {'clientes': clientes, 'unidades': unidades, 'documentos': documentos})

def get_progress(request):
    try:
        with open('progreso.txt', 'r') as f:
            progress = f.read().strip()
        print(f"Progreso leído: {progress}")
        return JsonResponse({'progress': int(progress)})
    except Exception as e:
        print(f"Error al obtener el progreso: {str(e)}")
        return JsonResponse({'error': f'Error al obtener el progreso: {str(e)}'})

