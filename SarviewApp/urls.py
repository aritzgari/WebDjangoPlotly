from re import template

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from SarviewApp import views

urlpatterns = [
    path('', LoginView.as_view(template_name="SarviewApp/login.html"), name="login"), #Ventana de login
    path('lista/', login_required(views.lista), name="lista"), #Ventana de lista de maquinas
    path('rodion/', login_required(views.rodion), name="rodion"), #Ventana de visualización de Rodion
    path('register/', login_required(views.register), name="register"), #Ventana de registro 
    path('logout/', LogoutView.as_view(template_name="SarviewApp/logout.html"), name="logout"), #Ventana de logout con funcionalidad de logout
    path('dashboard/', login_required(views.dashboard), name="dashboard"), #Ventana de visualización de datos de simulación versión nueva.
    path('datosplc/', login_required(views.plc), name="datosplc") # Ventana de visualización de datos de simulación versión nueva.
]