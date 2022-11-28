import time
from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

#
# Aqui se empieza a trabajar con los datos almacenados en el csv de Rodion.
#

# Lectura de datos del csv de Rodion
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

# Adapta los datos obtenidos a formato json para poder mostrarlos luego por html.
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
# Lectura de datos de simulación.
#

# Bajar los datos de la base de datos de influx.
def selectinflux(desde, hasta):

    #Para comparar.
    today = datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today = pd.to_datetime(today)
    mañana = pd.to_datetime(today) + timedelta(days=1)

    # Formatos compatibles entre la columna timestamp y las fechas seleccionadas.
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

    #Pasar de datetime a unix.
    desde = int(time.mktime(desde.timetuple()) * 1000000000)
    hasta = int(time.mktime(hasta.timetuple()) * 1000000000)

    # Generar el cliente de influx.
    client = InfluxDBClient(host='localhost', port=8086)

    # Seleccionar la base de datos concreta que tiene la información.
    client.switch_database('simulacion')

    # Hacer la query para seleccionar todo lo de la base de datos.
    result = client.query(f'SELECT * FROM "simulacion" where time > {desde} and time < {hasta}')

    # Coger los datos de medida de la base de datos.
    points = list(result.get_points(measurement='simulacion'))

    # Generar un dataframe del diccionario de la línea anterior.
    df = pd.DataFrame.from_dict(points)

    # Renombrar la columna de time para que sea compatible con el resto de funciones más adelante.
    df.rename(columns={'time': 'Timestamp'}, inplace=True)

    # Cambiar el formato de horas a uno que no tenga en cuenta la zona horaria.
    df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.tz_localize(None)

    # Cambiar el formato de datetime a string para mostrarlo más facil.
    df['Timestamp'] = df['Timestamp'].astype(str)

    client.close()

    return df

# Adaptar los datos leidos del simulador a json.
def adaptarsimu(desde,hasta):

    # Coger los datos de la BD de influx.
    datos = selectinflux(desde,hasta)

    # De dataframe a json para luego visualizar en html raw.
    eljson = datos.to_json(orient='records')

    # Devolver el json.
    return eljson

# Descargar los datos del simulados entre las fechas introducidas.
def descargarcsvdesdehasta(desde, hasta):

    # Llamar a filtrado con fechas.
    filtered_df = selectinflux(desde, hasta)

    # Dataframe vacio para sobreescribir el csv.
    df = pd.DataFrame()
    df.to_csv('SarviewApp/static/SarviewApp/temp/temp2.csv')

    # Pasar esos datos a un csv local.
    filtered_df.to_csv(
        'SarviewApp/static/SarviewApp/temp/temp2.csv', mode='a', sep=';')

# Pintar el gráfico con los datos en las fechas determinadas.
def plotlysimchoose(desde, hasta):

    # Filtrado según fechas.
    filtered_df = selectinflux(desde, hasta)

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


#
# Lectura de datos de plc.
#

#Conseguir la información desde influx.
def selectinfluxplc(desde,hasta):

   #Para comparar.
    today = datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today = pd.to_datetime(today)
    mañana = pd.to_datetime(today) + timedelta(days=1)

    # Formatos compatibles entre la columna timestamp y las fechas seleccionadas.
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

    #Pasar de datetime a unix
    desde = int(time.mktime(desde.timetuple()) * 1000000000)
    hasta = int(time.mktime(hasta.timetuple()) * 1000000000)

    # generar el cliente de influx.
    client = InfluxDBClient(host='localhost', port=8086)

    # Seleccionar la base de datos concreta que tiene la información.
    client.switch_database('plc')

    # Hacer la query para seleccionar todo lo de la base de datos.
    result = client.query(
        f'SELECT * FROM "plc" where time > {desde} and time < {hasta}')

    # Coger solo los datos de medida de la base de datos.
    points = list(result.get_points(measurement='plc'))

    # Generar un dataframe del diccionario generado en la línea anterior.
    df = pd.DataFrame.from_dict(points)

    # Renombrar la columna de time para que sea compatible con el resto de funciones más adelante.
    df.rename(columns={'time': 'Timestamp'}, inplace=True)

    # Cambiar el formato de horas a uno que no tenga en cuenta la zona horaria.
    df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.tz_localize(None)

    # Cambiar el formato de datetime a string para mostrarlo más facil.
    df['Timestamp'] = df['Timestamp'].astype(str)

    client.close()

    return df

# Adaptar los datos leidos del plc a json.
def adaptarplc(desde,hasta):

    # Coger los datos.
    datos = selectinfluxplc(desde,hasta)

    # De dataframe a json.
    eljson = datos.to_json(orient='records')

    # Devolver el json.
    return eljson

# Descargar los datos del plc entre las fechas introducidas.
def descargarcsvdesdehastaplc(desde, hasta):

    # Filtrar con fechas.
    filtered_df = selectinfluxplc(desde, hasta)

    # Dataframe vacio para sobreescribir el csv.
    df = pd.DataFrame()
    df.to_csv('SarviewApp/static/SarviewApp/temp/temp3.csv')

    # Pasar esos datos a un csv local.
    filtered_df.to_csv(
        'SarviewApp/static/SarviewApp/temp/temp3.csv', mode='a', sep=';')

# Pintar el gráfico con los datos en las fechas determinadas.
def plotlyplcchoose(desde, hasta):
    
    # Filtrado según fechas.
    filtered_df = selectinfluxplc(desde, hasta)

    # Poner como int para visualizar
    filtered_df["EntradaNode"] = filtered_df["EntradaNode"].astype(int)

    # Poner como int para visualizar
    filtered_df["Salida"] = filtered_df["Salida"].astype(int)

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
    fig.update_layout(font=dict(size=14),  title="Gráfico de datos de plc", yaxis_title='Valores',
                      xaxis_title='Fechas')

    # Solo visible los seleccionados                  
    #fig.for_each_trace(lambda trace: trace.update(visible="legendonly"))

    return fig
