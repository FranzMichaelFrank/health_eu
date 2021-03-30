import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import urllib.request as urllib
#from urllib.request import urlopen
import pandas as pd
import plotly.graph_objs as go
import statsmodels.api as sm
import plotly.figure_factory as ff
import numpy as np

mapbox_access_token = "pk.eyJ1Ijoic3RlZmZlbmhpbGwiLCJhIjoiY2ttc3p6ODlrMG1ybzJwcG10d3hoaDZndCJ9.YE2gGNJiw6deBuFgHRHPjg"
path = 'https://raw.githubusercontent.com/FranzMichaelFrank/health_eu/main/'
df = pd.read_csv(path + 'food_supply.csv', dtype={"id": str})
df_scatter = pd.read_csv(path + 'scatter_data.csv', dtype={"id": str})

url = path + "european-union-countries.geojson"
response = urllib.urlopen(url)
european_union = json.loads(response.read())

layout = dict(
    autosize=True,
    #automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# design for mapbox
bgcolor = "#f3f3f1"  # mapbox light map land color
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}

def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }

columns = df.iloc[:,2:22].columns
health_cols = ["Obesity", "Diabetes Prevalence", "Cardiovascular Death Rate", "Life Expectancy", "Health Expenditure" ]

# Create controls
behaviour_options = [
    dict(label=country, value=country)
    for country in columns]

dropdown_behaviour = dcc.Dropdown(
        id='candidate_radio',
        options=behaviour_options,
        value=columns[0],
    )


app = dash.Dash(__name__)

###
df_new = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
available_indicators = df_new['Indicator Name'].unique()
###


## FF ##
foods = ['Milk - Excluding Butter','Oilcrops', 'Eggs', 'Starchy Roots','Meat','Vegetables','Fruits - Excluding Wine','Aquatic Products, Other','Treenuts','Spices','Pulses','Alcoholic Beverages','Cereals - Excluding Beer','Animal fats','Vegetable Oils','Offals','Sugar & Sweeteners','Fish, Seafood','Stimulants','Smoking']
df_corr_round = df_scatter.corr()[["Obesity", "Diabetes Prevalence", "Cardiovascular Death Rate", "Life Expectancy", "Health Expenditure" ]].T[foods].T.round(2)
fig_cor = ff.create_annotated_heatmap(
            z=df_corr_round.to_numpy(),
            x=df_corr_round.columns.tolist(),
            y=df_corr_round.index.tolist(),
            zmax=1, zmin=-1,
            showscale=True,
            hoverongaps=True
            )
fig_cor.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
fig_cor.update_layout(yaxis_tickangle=-45)
fig_cor.update_layout(xaxis_tickangle=-45)
fig_cor.update_layout(title_text='',height=600)



health = df_scatter[["Country","Obesity", "Diabetes Prevalence", "Cardiovascular Death Rate", "Life Expectancy", "Health Expenditure" ]]



fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    x=health["Country"],
    y=health["Obesity"],
    name="Obesity (% of Population)",
    marker_color='#0d0887'
))
fig_bar.add_trace(go.Bar(
    x=health["Country"],
    y=health["Diabetes Prevalence"],
    name="Diabetes Prevalence (% of population)",
    marker_color='#7201a8'
))

fig_bar.add_trace(go.Bar(
    x=health["Country"],
    y=health["Cardiovascular Death Rate"],
    name="Cardiovascular Death Rate (per 100,000)",
    marker_color='#bd3786'
))

fig_bar.add_trace(go.Bar(
    x=health["Country"],
    y=health["Life Expectancy"],
    name="Life Expectancy",
    marker_color='#ed7953'
))

fig_bar.add_trace(go.Bar(
    x=health["Country"],
    y=health["Health Expenditure"],
    name="Health Expenditure (% of GDP)",
    marker_color='#fdca26'
))
# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig_bar.update_layout(barmode='group', xaxis_tickangle=-45)
fig_bar.update_layout(plot_bgcolor='white')
fig_bar.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey')
fig_bar.update_xaxes(showline=True, linewidth=2, linecolor='black')



## FF ##

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("Nova_IMS.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    "Food consumption characteristics of the countries in the EU",
                                    style={"margin-bottom": "0px","font-weight": "bold"},
                                ),
                                html.H5(
                                    "Analysis of the relationship between nutritional patterns and \n the health status within the countries", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="three column",
                    id="title",
                ),
                html.Div(
                    # create empty div for align cente
                    className="one-third column",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [

                        html.H6("Consumption by food type", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),

                        html.P(
                            "The cultures and customs of the 27 EU countries differ widely. Of course, the same applies to their eating habits." 
                            " On the map on the right, the eating preferences of the individual countries can be explored.",
                            className="control_label",style={"text-align": "justify"}
                        ),

                        html.P("Select nutrition category:", className="control_label"),
                        dropdown_behaviour,

                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",

                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P(id="well_text"), html.P("Maximum values"),
                                        html.P(id="max_name"),
                                        html.P(id="max_value"),
                                    ],
                                        className="mini_container",
                                        id="wells",
                                ),
                                html.Div(
                                    [html.P(id="gasText"), html.P("Minimum values"),
                                    html.P(id="min_name"),
                                     html.P(id="min_value"),
                                    ],
                                    className="mini_container",
                                    id="gas"
                                ),
                                html.Div(
                                    [html.P(id="oilText"), html.P("Mean values"),
                                     html.P("Country: /"),
                                     html.P(id="mean")]
                                    ,
                                    className="mini_container",
                                    id="oil",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="choropleth")],
                            #id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),

        html.Div(
            [
                html.H6("General health data of the countries", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                dcc.Graph(id="bar_chart", figure=fig_bar)
            ],
            className="row pretty_container",
        ),

        html.Div(
            [   html.Div(
                    [dcc.Graph(id="grap", figure=fig_cor)],
                    className="pretty_container four columns",
                ),
                html.Div(
                    [   html.H6("Correlations between food consumption and health", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                        
                        
                        html.P("Select nutrition category for x axis:", className="control_label"),
                        dcc.Dropdown(
                            id='xaxis-column',
                            options=[{'label': i, 'value': i} for i in columns],
                            value=columns[0]
                        ),
                        dcc.RadioItems(
                            id='xaxis-type',
                            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                            value='Linear',
                            labelStyle={'display': 'inline-block'}
                        ),
                        html.P("Select health variable for y axis:", className="control_label"),
                        dcc.Dropdown(
                            id='yaxis-column',
                            options=[{'label': i, 'value': i} for i in health_cols],
                            value=health_cols[1]
                        ),
                        dcc.RadioItems(
                            id='yaxis-type',
                            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                            value='Linear',
                            labelStyle={'display': 'inline-block'}
                        ),
                        dcc.Graph(id="indicator-graphic")
                    ],
                    
                    className="pretty_container eight columns",
                ),

                
            ],
            className="row flex-display",
        ),

        

        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="pie_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="aggregate_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),

        html.Div(
            [
                html.H4("Sources", style={"margin-top": "0"}),
                dcc.Markdown(
                    """\
                         - Dashboard written in Python using the [Dash](https://dash.plot.ly/) web framework.
                         - Parallel and distributed calculations implemented using the [Dask](https://dask.org/) Python library.
                         - Server-side visualization of the location of all 40 million cell towers performed 
                         using the [Datashader] Python library (https://datashader.org/).
                         - Base map layer is the ["light" map style](https://www.mapbox.com/maps/light-dark/)
                         provided by [mapbox](https://www.mapbox.com/).
                         - Cell tower dataset provided by the [OpenCelliD Project](https://opencellid.org/) which is licensed under a
                        [_Creative Commons Attribution-ShareAlike 4.0 International License_](https://creativecommons.org/licenses/by-sa/4.0/).
                         - Mapping from cell MCC/MNC to network operator scraped from https://cellidfinder.com/mcc-mnc.
                         - Icons provided by [Font Awesome](https://fontawesome.com/) and used under the
                        [_Font Awesome Free License_](https://fontawesome.com/license/free). 
                        """
                ),
            ],
            className="row pretty_container",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


####
@app.callback(
    Output("choropleth", "figure"),
    [Input("candidate_radio", "value")])
def display_choropleth(candi):
    fig = px.choropleth_mapbox(
        df, geojson=european_union, color=candi,
        locations="iso_a3", featureidkey="properties.gu_a3",
        center={"lat": 56.5, "lon": 11}, zoom=3)
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_accesstoken=mapbox_access_token)

    return fig


@app.callback(
    [
        Output("max_name", "children"),
        Output("max_value", "children"),
        Output("min_name", "children"),
        Output("min_value", "children"),
        Output("mean", "children"),
    ],
    [
        Input("candidate_radio", "value"),
    ]
)
def indicator(auswahl):
    max_id = df[auswahl].idxmax()
    min_id = df[auswahl].idxmin()

    max_value = df[auswahl].max()
    max_value = str(max_value)

    max_name = df.loc[max_id, 'Country']
    min_value = df[auswahl].min()
    min_value = str(min_value)

    min_name = df.loc[min_id, 'Country']
    mean = df[auswahl].mean()
    st_dev = df[auswahl].std()
    mean = round(mean, 2)
    mean = str(mean)

    BOLD = '\033'
    END = '\033'

    return "Country: " + max_name, max_value + "kg per capita per year",  \
           "Country: " + min_name, min_value + "kg per capita per year", \
           "Mean: " + mean + "kg per capita per year", 


@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
    Input('xaxis-type', 'value'),
    Input('yaxis-type', 'value'))
def update_graph(xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type):

    col_name = str(yaxis_column_name) + " (above Average)"
    df_scatter[col_name] = (df_scatter[yaxis_column_name] > df_scatter[yaxis_column_name].mean())

    fig = px.scatter(df_scatter, x=xaxis_column_name, y =yaxis_column_name, size="GDP per Capita", color=col_name, hover_name="Country", 
                    log_x=False,marginal_x = "box",marginal_y = "box", template="simple_white", color_discrete_sequence=["#0d0887", "#9c179e"])


    # linear regression
    regline = sm.OLS(df_scatter[yaxis_column_name],sm.add_constant(df_scatter[xaxis_column_name])).fit().fittedvalues

    # add linear regression line for whole sample
    fig.add_traces(go.Scatter(x=df_scatter[xaxis_column_name], y=regline,
                            mode = 'lines',
                            marker_color='#fb9f3a',
                            name='OLS Trendline')
                            )

    fig.update_layout(legend_x=0.8, legend_y=1)

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    #fig.update_xaxes(title=xaxis_column_name,
     #                type='linear' if xaxis_type == 'Linear' else 'log')

    #fig.update_yaxes(title=yaxis_column_name,
     #                type='linear' if yaxis_type == 'Linear' else 'log')

    return fig


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
