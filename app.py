import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import urllib.request as urllib#
#from urllib.request import urlopen
import pandas as pd
import plotly.graph_objs as go


mapbox_access_token = "pk.eyJ1Ijoic3RlZmZlbmhpbGwiLCJhIjoiY2ttc3p6ODlrMG1ybzJwcG10d3hoaDZndCJ9.YE2gGNJiw6deBuFgHRHPjg"
path = 'https://raw.githubusercontent.com/steffenhill/Dash/main/'
df = pd.read_csv(path + 'geoplot_final.csv', dtype={"id": str})

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

columns = df.iloc[:,2:20].columns
# Create controls
behaviour_options = [
    dict(label=country, value=country)
    for country in columns]





app = dash.Dash(__name__)




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
                            src=app.get_asset_url("dash-logo.png"),
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
                                html.H3(
                                    "New York Oil and Gas",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Production Overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
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
                        html.P(
                            "TEXTTEXTTEXTTEX TTEXTTEXTTEXTTEXTT TEXTTEXTTEXTT EXTTEXTTE XTTEXTTEXTT"
                            "EXTTEXT TEXTTEX TTEXTTEXTT EXTTEXT"
                            "EXTTEXT TEXTTEX TTEXTTEXTT EXTTEXT"
                            "EXTTEXT TEXTTEX TTEXTTEXTT EXTTEXT",
                            className="control_label",
                        ),

                        html.P("Filter by well type:", className="control_label"),
                        dcc.RadioItems(
                                id='candidate_radio',
                                options=[{'value': x, 'label': x}
                                         for x in columns],
                                value=columns[0],
                                labelStyle={'display': 'inline-block'}
                            ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="well_text"), html.P("No. of Wells")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="gasText"), html.P("Gas")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oilText"), html.P("Oil")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="waterText"), html.P("Water")],
                                    id="water",
                                    className="mini_container",
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
                html.Div(
                    children=[
                        dcc.Input(id='input', type='text'),
                        dcc.Graph(id='plot')],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="individual_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),

        html.Div(
            children=[
                html.H4(
                    [
                        "Locations",
                    ],
                    className="container_title",
                ),
                dcc.Graph(
                    id="map-graph",
                    figure=blank_fig(row_heights[1]),
                    config={"displayModeBar": False},
                ),
                html.Button(
                    "Reset View", id="reset-map", className="reset-button",
                    style={
                        "width": "100%",
                        "margin-top": "10",
                        "height": "30",
                        "line - height": "30",
                    },
                ),
            ],
            className="row pretty_container",
            id="map-div",
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
                html.H4("Acknowledgements", style={"margin-top": "0"}),
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
            style={
                "width": "98%",
                "margin-right": "0"
            },
            className="twelve columns pretty_container",
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
    Output('plot', 'figure'),
    [Input('input', 'value')]
)
def update_graph_1(input):
    return {'data':[go.Bar(
            x=['giraffes', 'orangutans', 'monkeys'],
            y=[20, 14, 23])]}


if __name__ == '__main__':
    app.run_server(debug=True)
