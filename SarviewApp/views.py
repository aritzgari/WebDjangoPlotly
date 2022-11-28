
from datetime import datetime, timedelta
import json
from django.shortcuts import render, redirect
from django.contrib import messages

from SarviewApp.funciones import adaptar, adaptarplc, adaptarsimu, descargarcsvdesdehasta, descargarcsvdesdehastaplc, plotly, descargarcsvdia, plotlyplcchoose, plotlysimchoose
from .forms import UserRegisterForm

#View de login.
def login(request):
    
    return render(request, "SarviewApp/login.html")

#View de registrarse.
def register(request):

    #Forma de realizar un registro de usuario "personalizado" para django.
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            messages.success(request, f'Usuario {username} creado')
            return redirect('lista')
    else:
        form = UserRegisterForm()
    context = {'form': form}

    return render(request, "SarviewApp/register.html", context)

#View de lista de dispositivos, ventana inicial del programa.
def lista(request):
    
    
    return render(request,"SarviewApp/lista.html")

#View especifica de rodion.
def rodion(request):
    
    #Leer csv adaptar y pasar a json.
    eljson = adaptar()
    eljson = json.loads(eljson)

    #Importar el gráfico de plotly.
    elplot = plotly()
    
    #Pasarlo a html.
    chart = elplot.to_html(config={'displaylogo': False})

    #Darles un nombre al que llamar en el html.
    context = {'d': eljson,'chart': chart}

    #Descarga un excel con los datos del día.
    descargarcsvdia()

    return render(request,"SarviewApp/rodion.html",context)


#View de dashboard diferente al anterior con request de fechas.
def dashboard(request):
    
    #Crear desde hasta.
    desde = datetime.now()
    desde = desde.replace(hour=0, minute=0, second=0, microsecond=0)
    hasta = desde + timedelta(days=1)

    #Si se ha hecho el request se sobreescribe por los valores por defecto.
    if request.GET:
        desde = request.GET['desde']
        hasta = request.GET['hasta']

    #Descargar csv del simulador.
    descargarcsvdesdehasta(desde,hasta)

    #El plot del dataframe de la simulación.
    elplot = plotlysimchoose(desde,hasta)

    #Pasarlo a html. La parte de config te permite quitar el logo con la publi de plotly.
    chart = elplot.to_html(config={'displaylogo': False})

    #Adaptar lo leido del csv al completo para mostrarlo en html.
    eljson = adaptarsimu(desde,hasta)
    eljson = json.loads(eljson)

    #Darles un nombre al que llamar en el html.
    context = {'d': eljson, 'chart': chart}

    return render(request, "SarviewApp/dashboard.html", context)

#View de dashboard con datos plc y request de fechas.
def plc(request):

    #Crear desde hasta.
    desde = datetime.now()
    desde = desde.replace(hour=0, minute=0, second=0, microsecond=0)
    hasta = desde + timedelta(days=1)

    #Si se ha hecho el request se sobreescribe por los valores por defecto.
    if request.GET:
        desde = request.GET['desde']
        hasta = request.GET['hasta']

    #Descargar csv del simulador.
    descargarcsvdesdehastaplc(desde, hasta)

    #El plot del dataframe de la simulación.
    elplot = plotlyplcchoose(desde, hasta)

    #Pasarlo a html. La parte de config te permite quitar el logo con la publi de plotly.
    chart = elplot.to_html(config={'displaylogo': False})

    #Adaptar lo leido del csv al completo.
    eljson = adaptarplc(desde, hasta)
    eljson = json.loads(eljson)

    #Darles un nombre al que llamar en el html.
    context = {'d': eljson, 'chart': chart}

    return render(request, "SarviewApp/datosplc.html", context)
