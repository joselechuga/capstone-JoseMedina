from django.urls import path

from techflow.views import index


urlpatterns = [
    path('', index),
]