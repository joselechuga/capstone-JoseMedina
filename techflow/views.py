import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse



def custom_404(request, exception):
    return render(request, '404.html',{})

def index(request):
    try:
        return render(request, 'index.html')
    
    except Exception as e:
        return render(request, 'error.html', {'error_message': str(e)})

# Login para verificar el acceso a panel
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return render(request, 'index.html')
        else:
            return render(request, 'login.html', {'error_message': 'Credenciales incorrectas!'})

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
