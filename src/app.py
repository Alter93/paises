# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cc import ISO3166
from plots import get_map, get_line_chart

# Incorporate data
inmigracion = pd.read_csv("src/datos/inmigracion.tsv", sep=r'\,|\t', engine='python', dtype=str)
poblacion = pd.read_csv("src/datos/population.tsv", sep=r'\,|\t', engine='python', dtype=str)
gdp_per_capita = pd.read_csv("src/datos/gdp_per_capita.tsv", sep=r'\,|\t', engine='python', dtype=str)
purchase_power = pd.read_csv("src/datos/purchase_power.tsv", sep=r'\,|\t', engine='python', dtype=str)
new_residence = pd.read_csv("src/datos/new_residence.tsv", sep=r'\,|\t', engine='python', dtype=str)
desempleo_miles = pd.read_csv("src/datos/desempleo_miles.tsv", sep=r'\,|\t', engine='python', dtype=str)
nacidos_extranjero = pd.read_csv("src/datos/nacidos_extranjero.tsv", sep=r'\,|\t', engine='python', dtype=str)
balance_remesas = pd.read_csv("src/datos/balance_remesas.tsv", sep=r'\,|\t', engine='python', dtype=str)

datasets = { 
    "inmigracion": inmigracion,
    "poblacion": poblacion,
    "gdp_per_capita":gdp_per_capita,
    "purchase_power":purchase_power,
    "new_residence":new_residence,
    "desempleo_miles":desempleo_miles,
    "nacidos_extranjero":nacidos_extranjero,
    "balance_remesas":balance_remesas
}

years = []
for i in range(14,23):
    year = f"{2000 + i}"
    for key in datasets.keys():
        df = datasets[key]
        df[year] = df[year].str.replace(r"p|b|e", '', regex=True)
        df[year] = pd.to_numeric(df[year], errors='coerce')
    years.append(year)

for key in datasets.keys():
    df = datasets[key]
    df = df[df.geo != 'UK'].copy()
    df.set_index('geo', inplace=True)
    df['country_name'] = df.index.map(ISO3166)
    datasets[key] = df

table_data = datasets["inmigracion"][["country_name","2022"]].sort_values(by="2022", ascending=False).to_dict("records")

for rec in table_data:
    rec["2022"] = f'{int(rec["2022"]):,}'

# Initialize the app
app = Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)

server = app.server

economia_options = [
    {"value": "gdp_per_capita", "label": "PIB per cápita"},
    {"value": "purchase_power", "label": "Poder adquisitivo"},
    {"value": "desempleo_miles", "label": "Tasa de desempleo (por cada 1000 hab.)"},
    {"value": "balance_remesas", "label": "Remesas"},
]

migracion_options = [
    {"value": "inmigracion", "label": "Total migrantes"},
    {"value": "new_residence", "label": "Motivos migratorios"},
    {"value": "nacidos_extranjero", "label": "Poblacion nacida en el extrajero"}  
]
# App layout
app.layout = [
    html.H2("EFECTOS DE LA MIGRACION EN LA ECONOMIA DE LA UE"),
    html.Hr(),
    html.Div(
        className="row",
        children=[
            html.Div(
                className='eight columns div-for-charts',
                children=[dcc.Graph(figure=get_map(datasets), id='mapa',style={'width': '90%', 'height': '70vh'})]
            ),
            html.Div(
                className='four columns div-for-charts',
                children=[
                    dash_table.DataTable(
                        data = table_data,
                        columns=[
                            {'id': 'country_name', 'name': 'Pais'}, 
                            {'id': '2022', 'name': 'Inmigrantes por año'}
                        ],
                        page_size=20, 
                        style_table={'width': '90%', 'height': '70vh'},
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'color': 'white'
                        },
                        style_data={
                            'backgroundColor': 'rgb(50, 50, 50)',
                            'color': 'white'
                        },
                    )
                ]
            )
        ]
    ),
    html.Div(
        className="row div-user-controls",
        children=[
            html.Div(
                className='four columns div-for-dropdown',
                children=[
                    dcc.Dropdown(
                        id="migracion-dropdown",
                        options=migracion_options,
                        multi=True,
                        placeholder="Selecciona una métrica",
                    )
                ]
            ),
            html.Div(
                className='four columns div-for-dropdown',
                children=[
                    dcc.Dropdown(
                        id="economia-dropdown",
                        options=economia_options,
                        multi=True,
                        placeholder="Selecciona una métrica",
                    )
                ]
            )
        ]
    ),
    html.Div(
        className="row",
        children=[
            html.Div(
                className='div-for-charts',
                children=[dcc.Graph(id='linea-1', style={'width': '100%', 'height': '50vh'})]
            ),
        ]
    )
]

@app.callback(
    Output("linea-1", "figure"),
    [
        Input("mapa", "clickData"),
        Input("economia-dropdown", "value"),
        Input("migracion-dropdown", "value"),
    ]
)
def actualizar_lineas(mapa, economia, migracion):
    values = []
    if mapa is None:
        country = "European Union (27 countries)"
    else:
        country = mapa["points"][0]["location"]

    if economia is not None:
        for i in economia_options:
            if i["value"] in economia:
                values.append(i)

    if migracion is not None:
        for i in migracion_options:
            if i["value"] in migracion:
                values.append(i)

    if len(values) > 0:
        return get_line_chart(datasets, country, years, metric = values)
    else:
        return get_line_chart(datasets, country, years)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)


