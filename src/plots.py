import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def get_map(datasets):
    inm_df = datasets['inmigracion']
    pop_df = datasets['poblacion']
    inm_df["porcentual"] = inm_df["2022"] / pop_df['2022']

    fig = px.scatter_geo(
        inm_df[inm_df.country_name != 'European Union (27 countries)'][["country_name","2022",'porcentual']], 
        locations="country_name",
        locationmode='country names', 
        hover_name="country_name",
        color='2022',
        color_continuous_scale='viridis', 
        size="porcentual",
        projection="equirectangular",
    )

    fig.update_layout(
        template='plotly_dark'
    )

    fig.update_geos(
        visible=False, 
        resolution=50,
        showcountries=True,
        countrycolor="#888",
        scope='europe',
        showland=True, 
        landcolor="#111",
    )

    return fig


def get_line_chart(datasets, country, years, metric=[{"value": "inmigracion", "label": "Total migrantes"},{"value": "purchase_power", "label": "Poder adquisitivo"}]):
    
    lines = []
    subtitle = ""
    for met in metric:
        if met["value"] == "new_residence":
            df = datasets[met["value"]].copy()
            df["index_new"] = df.index + "-" + df["reason"]
            df.set_index('index_new', inplace=True)
            lines.append({"df": df, "label": met["label"] })
        else:
            lines.append({"df": datasets[met["value"]], "label": met["label"] })

        if subtitle == "":
            subtitle = met["label"]
        else:
            subtitle = subtitle + ", " + met["label"]
            
    cc = ""
    fig_df = pd.DataFrame(index = years)
    print(fig_df)
    for df in lines:
        data = df["df"]
        df["df"] = data[data.country_name == country][years].transpose()
        try:
            cc = list(df["df"].columns)
        except:
            continue


        for code in cc:
            if len(cc) > 1:
                col_name = df["label"] + " - " + code.split("-")[1]
                fig_df[col_name] = df["df"][code] / df["df"][code].abs().max()
            else:
                fig_df[df["label"]] = df["df"][code] / df["df"][code].abs().max()



    fig = px.line(fig_df)


    fig.update_layout(
        template='plotly_dark',
        title=dict(
            text=country
        ),
        title_subtitle=dict(
            text=subtitle
        ),
        xaxis=dict(
            title=dict(
                text='Año'
            )
        ),
        yaxis=dict(
            visible=False,
            title=dict(
                text=''
            )
        ),
    )

    return fig