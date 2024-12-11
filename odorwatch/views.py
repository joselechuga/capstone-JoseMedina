import os
import requests
import subprocess
import logging
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from .models import Cliente,UnidadFiscalizable,Documento, Coincidencias

import signal
from django.contrib.auth.models import User
from .forms import UserForm
from django.contrib import messages

# Variable global para almacenar el PID del proceso
process_pid = None

def custom_404(request, exception):
    return render(request, '404.html',{})

# Login para verificar el acceso a panel
@csrf_exempt
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Autenticar al usuario basado en el correo
        user = None
        if username == 'jmedina@tsgenviro.com':
            user = authenticate(request, username='superuser_username', password='superuser_password')
        elif username == 'captsonejose@tsgenviro.com':
            user = authenticate(request, username='captsonejose', password='normal_user_password')
        else:
            user = authenticate(request, username=username, password=password)
        
        if user is not None:
            request.session['user_email'] = user.email
            login(request, user)
            print(f"Usuario autenticado: {user.email}")  # Mensaje de depuración
            return redirect('home')
        elif 'correo' in request.POST and 'firma' in request.POST and 'certificado' in request.POST:
            correo = request.POST.get('correo')
            firma = request.POST.get('firma')
            certificado = request.POST.get('certificado')
            data = {'user_email': correo, 
                    'firma': firma, 
                    'certificado': certificado
                    }
            # Buscar usuario por correo
            try:
                user = User.objects.get(email=correo)
                request.session['user_email'] = correo
                login(request, user)
                return redirect('home')
            except User.DoesNotExist:
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
    m365_user_email = request.session.get('m365_user_email', 'Correo M365 no disponible')  # Asegurate de almacenar este correo en la sesión

    # Comparar los correos
    email_coincide = user_email == m365_user_email

    # Añadir los datos al contexto
    context = {
        'user_email': user_email,
        'm365_user_email': m365_user_email,
        'email_coincide': email_coincide
    }

    return render(request, 'home.html', context)


def run_script(request):
    """Ejecuta el script main.py y devuelve la salida."""
    global process_pid
    try:
        # Ejecuta el script main.py
        process = subprocess.Popen(
            ['python', 'modulos/main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        process_pid = process.pid  # Almacena el PID del proceso
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args, output=stdout, stderr=stderr)
        
        # Retorna JSON
        return JsonResponse({'output': stdout})
    except subprocess.CalledProcessError as e:
        # Captura errores de ejecución del script
        return JsonResponse({'error': f'Error al ejecutar el script: {e.stderr}'})
    except Exception as e:
        # Captura cualquier otro error
        return JsonResponse({'error': f'Error inesperado: {str(e)}'})

def stop_script(request):
    """Detiene la ejecución del script main.py."""
    global process_pid
    try:
        if process_pid is not None:
            os.kill(process_pid, signal.SIGTERM)  # Envía la señal de terminación
            process_pid = None  # Resetea el PID
            return JsonResponse({'message': 'Script detenido exitosamente.'})
        else:
            return JsonResponse({'error': 'No hay un script en ejecución.'})
    except Exception as e:
        return JsonResponse({'error': f'Error al detener el script: {str(e)}'})

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
    coincidencias = Coincidencias.objects.all()
    return render(request, 'snifa.html', {'clientes': clientes, 'unidades': unidades, 'documentos': documentos, 'coincidencias':coincidencias})

def get_progress(request):
    try:
        with open('progreso.txt', 'r') as f:
            progress = f.read().strip()
        print(f"Progreso leído: {progress}")
        return JsonResponse({'progress': int(progress)})
    except Exception as e:
        print(f"Error al obtener el progreso: {str(e)}")
        return JsonResponse({'error': f'Error al obtener el progreso: {str(e)}'})

def mostrar_ejecuciones(request):
    log_file_path = os.path.join('modulos', 'logs', f'{time.strftime("%Y-%m-%d")}.lst')
    logs = []

    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            logs = log_file.readlines()[-10:]  # Leer las últimas 10 líneas

    return render(request, 'home.html', {'logs': logs})

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def add_usuario(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Encripta la contraseña
            
            # Verifica las casillas de verificación
            if 'is_superuser' in request.POST and 'is_not_superuser' not in request.POST:
                user.is_superuser = True
            elif 'is_not_superuser' in request.POST and 'is_superuser' not in request.POST:
                user.is_superuser = False
            else:
                # Maneja el caso donde ambas o ninguna casilla están marcadas
                return render(request, 'add_usuario.html', {'form': form, 'error_message': 'Seleccione solo una opción para el rol de superuser.'})
            
            user.is_staff = user.is_superuser  # Opcional: Asigna el rol de staff si es superuser
            user.save()
            return redirect('add_usuario') 
    else:
        form = UserForm()
    
    usuarios = User.objects.all()  # Obtiene todos los usuarios
    return render(request, 'add_usuario.html', {'form': form, 'usuarios': usuarios})

def base_view(request):
    # Obtener el correo de la sesión
    user_email = request.session.get('user_email', 'Correo no disponible')
    m365_user_email = request.session.get('m365_user_email', 'Correo M365 no disponible')

    # Mensajes de depuración
    print(f"Correo del usuario: {user_email}")
    print(f"Correo M365: {m365_user_email}")

    # Comparar los correos
    email_coincide = user_email == m365_user_email

    # Añadir los datos al contexto
    context = {
        'user_email': user_email,
        'm365_user_email': m365_user_email,
        'email_coincide': email_coincide
    }

    return render(request, 'layouts/base.html', context)

@user_passes_test(is_superuser)
def edit_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            # Solo establece una nueva contraseña si se proporciona
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])  # Encripta la nueva contraseña si se proporciona
            # Verifica las casillas de verificación
            if 'is_superuser' in request.POST and 'is_not_superuser' not in request.POST:
                user.is_superuser = True
            elif 'is_not_superuser' in request.POST and 'is_superuser' not in request.POST:
                user.is_superuser = False
            user.is_staff = user.is_superuser  # Opcional: Asigna el rol de staff si es superuser
            user.save()
            return redirect('add_usuario')
    else:
        form = UserForm(instance=user)
    
    return render(request, 'add_usuario.html', {'form': form, 'usuarios': User.objects.all()})

@user_passes_test(is_superuser)
def delete_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'Usuario {user.username} eliminado exitosamente.')
        return redirect('add_usuario')
    return render(request, 'add_usuario.html', {'usuarios': User.objects.all()})