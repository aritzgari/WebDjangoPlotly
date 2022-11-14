from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

#
# Aqui se empieza a trabajar con los datos almacenados en el csv de Rodion.
#

# Primera lectura de los datos.
def leer():
    # Leer datos de csv.
    datos = pd.read_csv(
        "/home/aritz/Público/csv_a_html/Rodion.csv", sep=";", engine="python")

    # Renombrar columnas.
    dict = {'Europe/Madrid_datetime': 'datetime', 'Rodion 1, tachometer pulses': 'tachometer1', 'Rodion 1, temperature': 'temperature1',
            'Rodion 2, tachometer pulses': 'tachometer2', 'Rodion 2, temperature': 'temperature2', 'Rodion 3, tachometer pulses': 'tachometer3', 'Rodion 3, temperature': 'temperature3'}
    datos.rename(columns=dict, inplace=True)

    # Cambiar tipo de dato object a datetime.
    datos['datetime'] = pd.to_datetime(
        datos['datetime'], format='%d/%m/%Y %H:%M:%S')

    # Set timestamp as index.
    datos = datos.set_index('timestamp')

    # Eliminación de datos vacios.
    datos = datos.dropna()

    # Dropear minutos duplicados.
    datos['datetime'] = datos['datetime'].dt.floor('Min')
    datos = datos.drop_duplicates(subset=['datetime'])

    # Dropear datos de 0.
    datos = datos[datos.tachometer1 != 0.0]

    result = datos

    return result

# Adapta los datos a json.
def adaptar():

    # Coger los datos.
    datos = leer()

    # Pasar de datetime a string para que no lea una número.
    datos['datetime'] = datos['datetime'].astype(str)

    # De dataframe a json.
    eljson = datos.to_json(orient='records')

    # Devolver el json.
    return eljson

# Preparar el gráfico con los datos.
def plotly():

    # Leer los datos en dataframe.
    datos = leer()

    # Cambiar el dataframe de width a long.
    modolong = pd.melt(datos, id_vars='datetime')

    # Especificar los nombres.
    diccionarionombres = {
        "datetime": "Fechas",
        "value": "Valores",
        "variable": "Variables"
    }

    # Crear la figura sencilla de plotly.
    fig = px.line(modolong, x='datetime', y='value', color='variable',
                  title="Gráfico de datos de Rodion", labels=diccionarionombres, )
    fig.for_each_trace(lambda trace: trace.update(visible="legendonly"))

    return fig

# Descargar un csv con los datos tal cual.
def descargarcsvdia():

    # Leer los datos disponibles.
    datos = leer()

    # Pasar los datos a un csv para descargar.
    datos.to_csv('SarviewApp/static/SarviewApp/temp/temp.csv',
                 mode='a', sep=';')

#
# Aqui empiezan los datos de simulación.
#

# Bajar los datos de la base de datos de influx.
def selectinflux():

    # generar el cliente de influx.
    client = InfluxDBClient(host='localhost', port=8086)

    # Seleccionar la base de datos concreta que tiene la información.
    client.switch_database('simulacion')

    # Hacer la query para seleccionar todo lo de la base de datos.
    result = client.query('SELECT * FROM "simulacion"')

    # Coger solo los datos de medida de la base de datos.
    points = list(result.get_points(measurement='simulacion'))

    # Generar un dataframe del diccionario generado en la línea anterior.
    df = pd.DataFrame.from_dict(points)

    # Renombrar la columna de time para que sea compatible con el resto de funciones más adelante.
    df.rename(columns={'time': 'Timestamp'}, inplace=True)

    # Cambiar el formato de horas a uno que no tenga en cuenta la zona horaria.
    df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.tz_localize(None)

    # Cambiar el formato de datetime a string para mostrarlo más facil.
    df['Timestamp'] = df['Timestamp'].astype(str)

    return df

# Adaptar los datos leidos del simulador a json.
def adaptarsimu():

    # Coger los datos.
    datos = selectinflux()

    # De dataframe a json.
    eljson = datos.to_json(orient='records')

    # Devolver el json.
    return eljson

# Pintar el gráfico con los datos del día del simulador versión.
def plotlysim():

    # Leer datos de la simulacion.
    datos = selectinflux()

    # Datos de solo hoy.
    today = datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today + timedelta(days=1)

    # Formatos compatibles.
    datos['Timestamp'] = pd.to_datetime(
        datos['Timestamp'])
    today = pd.to_datetime(today)
    end_date = pd.to_datetime(end_date)

    # Filtra mayor que hoy a las 00:00:00 menor que mañana 00:00:00.
    filtered_df = datos.loc[(datos['Timestamp'] >= today)
                            & (datos['Timestamp'] < end_date)]

    # Cambiar el dataframe de width a long.
    modolong = pd.melt(filtered_df, id_vars='Timestamp')

    # Especificar los nombres.
    diccionarionombres = {
        "Timestamp": "Fechas",
        "value": "Valores",
        "variable": "Variables"
    }

    # Crear la figura sencilla de plotly.
    fig = px.line(modolong, x='Timestamp', y='value', color='variable',
                  title="Gráfico de datos de simulación", labels=diccionarionombres)
    
    # Solo visible al seleccionar.
    fig.for_each_trace(lambda trace: trace.update(visible="legendonly"))

    return fig

# Descargar csv de los datos del simulador.
def descargarcsvsimu():

    # Leer datos de la simulación
    datos = selectinflux()

    # Pasar esos datos a un csv local
    datos.to_csv('SarviewApp/static/SarviewApp/temp/temp2.csv',
                 mode='a', sep=';')

#
# Aquí empieza la simulación de fechas concretas.
#
def fechasconcretas(desde, hasta):

    # Leer datos de la simulación.
    datos = selectinflux()

    # Datos base de hoy y mañana.
    today = datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today = pd.to_datetime(today)
    mañana = pd.to_datetime(today) + timedelta(days=1)

    # Formatos compatibles.
    datos['Timestamp'] = pd.to_datetime(datos['Timestamp'])
    desde = pd.to_datetime(desde)
    hasta = pd.to_datetime(hasta) + timedelta(days=1)

    # Adaptación de fechas para que no sean imposibles.
    if hasta >= today:
        hasta = mañana
    if desde >= today:
        hasta = mañana
        desde = today
    if desde == hasta and desde != today:
        hasta = pd.to_datetime(hasta) + timedelta(days=1)

    # Filtrar por fechas.
    filtered_df = datos.loc[(datos['Timestamp'] >= desde)
                            & (datos['Timestamp'] < hasta)]
    return filtered_df

# Descargar los datos del simulados entre las fechas introducidas.
def descargarcsvdesdehasta(desde, hasta):

    # Filtrar con fechas.
    filtered_df = fechasconcretas(desde, hasta)

    # Dataframe vacio para sobreescribir el csv.
    df = pd.DataFrame()
    df.to_csv('SarviewApp/static/SarviewApp/temp/temp3.csv')

    # Pasar esos datos a un csv local.
    filtered_df.to_csv(
        'SarviewApp/static/SarviewApp/temp/temp3.csv', mode='a', sep=';')

# Pintar el gráfico con los datos en las fechas determinadas.
def plotlysimchoose(desde, hasta):

    # Filtrado según fechas.
    filtered_df = fechasconcretas(desde, hasta)

    # Cambiar el dataframe de width a long.
    modolong = pd.melt(filtered_df, id_vars='Timestamp')

    # Especificar los nombres.
    diccionarionombres = {
        "Timestamp": "Fecha",
        "value": "Valor",
        "variable": "Variable"
    }

    # Crear la figura sencilla de plotly.
    fig = px.line(modolong, x='Timestamp',
                  labels=diccionarionombres, y='value', color='variable')

    # Cambios en el gráfico.
    fig.update_layout(font=dict(size=14),  title="Gráfico de datos de simulación", yaxis_title='Valores',
                      xaxis_title='Fechas')
    
    return fig
