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
    # Obtener el correo de la sesión
    user_email = request.session.get('user_email', 'Correo no disponible')
    
    # Aquí puedes usar 'user_email' como lo desees, por ejemplo, mostrarlo en el template
    return render(request, 'home.html', {'user_email': user_email})

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
            return render(request, 'home.html', {'user_email': user.email})
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
                return render(request, 'home.html', data)
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