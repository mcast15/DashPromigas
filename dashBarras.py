import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output
import os

# Registros de Aves
aves = pd.read_csv("aves_100k_.csv")
# Registros de Plantas
plantas = pd.read_csv("plantitas800k.csv")

# Conteo de aves
conteo_Aves = aves['stateProvince'].value_counts()
df_conteoA = pd.DataFrame(conteo_Aves)
df_conteoA.columns = ['Cantidad de Aves']

# Conteo de plantas
conteo_Plantas = plantas['stateProvince'].value_counts()
df_conteoP = pd.DataFrame(conteo_Plantas)
df_conteoP.columns = ['Cantidad de Plantas']

# Combinar los DataFrames
df_combinado = pd.merge(df_conteoP, df_conteoA, left_index=True, right_index=True)
df_combinado = df_combinado.rename(columns={'stateProvince': 'Departamento'})

# Obtener la lista de departamentos únicos de aves y plantas
departamentos_aves = aves['stateProvince'].unique()
departamentos_plantas = plantas['stateProvince'].unique()

# Diseño de la aplicación
app = dash.Dash(__name__)

# Datos del nuevo gráfico de barras
cant = aves["iucnRedListCategory"].value_counts()
categorias = cant.index

# Colores personalizados para el gráfico de barras de aves
colores = ["#c2e96a", "#84c12d", "#39821E", "#07635F", "#073d4f"]

# Gráfico de barras de aves
fig_aves = px.bar(x=categorias, y=cant, color=categorias, color_discrete_sequence=colores)
fig_aves.update_layout(
    xaxis_title="Categorías",
    yaxis_title="Cantidad de especies",
    title="Categorías de riesgo en Aves"
)

# Datos del nuevo gráfico de barras de plantas
cantP = plantas["iucnRedListCategory"].value_counts()
categoriasP = cantP.index

# Gráfico de barras de plantas
fig_plantas = px.bar(x=categoriasP, y=cantP, color=categoriasP, color_discrete_sequence=colores)
fig_plantas.update_layout(
    xaxis_title="Categorías",
    yaxis_title="Cantidad de especies",
    title="Categorías de riesgo en Plantas"
)

# Función para filtrar y guardar el DataFrame por departamento
def filtroDepartamento(dataframe, departamento, path):
    df_filtrado = dataframe[dataframe['stateProvince'] == departamento]
    df_filtrado.to_csv(path, index=False)

# Agregar la opción "Selecciona un departamento..." al inicio de la lista de departamentos de aves y plantas
departamentos_aves = ["Selecciona un Departamento..."] + list(departamentos_aves)
departamentos_plantas = ["Selecciona un Departamento..."] + list(departamentos_plantas)

# Obtener el número de registros en el DataFrame de plantas
num_registros_plantas = len(plantas)
# Obtener el número de registros en el DataFrame de plantas
num_registros_aves = len(aves)

# Diseño de la aplicación
# Diseño de la aplicación
app.layout = html.Div(
    style={"background-color": "lightgray", "padding": "10px"},
    children=[
        html.Div(
            style={"background-color": "white", "padding": "10px", "font-weight": "bold", "width": "300px"},
            children=[
                html.Div(f"Número de registros en Plantas:\n {num_registros_plantas}"),
                html.Div(f"Número de registros en Aves: {num_registros_aves}")
            ]
        ),
        html.H1("Cantidad de Plantas y Aves por Departamento"),
        dcc.RadioItems(
            id="radio-tipo",
            options=[
                {"label": "Aves", "value": "aves"},
                {"label": "Plantas", "value": "plantas"}
            ],
            value="aves",
            labelStyle={"display": "inline-block"}
        ),
        dcc.Dropdown(
            id="dropdown",
            options=[],
            value="Selecciona un Departamento...",
            clearable=False,
        ),
        dcc.Graph(
            figure=px.bar(
                df_combinado,
                x=df_combinado.index,
                y=["Cantidad de Plantas", "Cantidad de Aves"],
                color_discrete_sequence=["#39821E", "#84c12d"],
            ),
        ),
        dcc.Graph(
            figure=fig_aves
        ),
        dcc.Graph(
            figure=fig_plantas
        ),
        html.Button("Descargar CSV", id="btn-descargar"),
        html.A(id="enlace-descarga", style={"display": "none"}),
    ]
)

# Función de callback para actualizar el dropdown de departamentos según el tipo seleccionado (aves o plantas)
@app.callback(
    Output("dropdown", "options"),
    Input("radio-tipo", "value")
)
def actualizar_departamentos(tipo):
    if tipo == "aves":
        return [{"label": dep, "value": dep} for dep in departamentos_aves]
    elif tipo == "plantas":
        return [{"label": dep, "value": dep} for dep in departamentos_plantas]
    else:
        return []

# Función de callback para manejar el evento del botón de descarga
@app.callback(
    Output("enlace-descarga", "href"),
    Input("btn-descargar", "n_clicks"),
    Input("dropdown", "value"),
    Input("radio-tipo", "value"),
    prevent_initial_call=True
)
def descargar_csv(n_clicks, departamento, tipo):
    if n_clicks is not None and departamento != "Selecciona un Departamento...":
        if tipo == "aves":
            dataframe = aves
            archivo = f"aves_{departamento.lower().replace(' ', '_')}.csv"
        elif tipo == "plantas":
            dataframe = plantas
            archivo = f"plantas_{departamento.lower().replace(' ', '_')}.csv"
        else:
            return None
        
        filtroDepartamento(dataframe, departamento, archivo)
        return "/" + archivo

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
