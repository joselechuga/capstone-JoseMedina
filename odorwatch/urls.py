from django.urls import path, include
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from . import views


urlpatterns = [

    path('', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('panel/', login_required(views.panel), name='panel'),
    path('index/', views.index, name='index'),
]