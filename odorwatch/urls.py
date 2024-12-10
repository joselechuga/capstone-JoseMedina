from django.urls import path, include
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from . import views


urlpatterns = [

    path('', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('panel/', login_required(views.panel), name='panel'),
    path('home/', views.home, name='home'),
    path('run-script/', views.run_script, name='run_script'),
    path('stop-script/', views.stop_script, name='stop_script'),
    path('get-logs/', views.get_logs, name='get_logs'),
    path('snifa/', views.snifa, name='snifa'),
    path('get-progress/', views.get_progress, name='get_progress'),
    path('ejecuciones/', views.mostrar_ejecuciones, name='mostrar_ejecuciones'),
    path('add_usuario/', views.add_usuario, name='add_usuario'),

]