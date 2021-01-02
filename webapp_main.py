import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from cell_coloring import construct_cell_color
from dash.dependencies import Input, Output
from dash_table.Format import Format, Scheme, Symbol, Group
import dash_table
import dash_bootstrap_components as dbc
from table_filter import split_filter_part
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from text_info import what_is_this, usage, more_info

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
# Meta tags help mobile render
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,    meta_tags=[
                {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}])

PAGE_SIZE = 50

setu = pd.read_csv("assets/SETU_ALL_2020.csv").drop(columns=["Unnamed: 0"])
score_fmt = Format().scheme(Scheme.fixed).precision(2)
columns = [
    {'name': 'code', 'id': 'code'},
    {'name': 'Unit Code', 'id': 'unit_code'},
    {'name': 'Level', 'id': 'Level', 'type': 'numeric'},
    {'name': 'Semester       ', 'id': 'Semester'},
] + [
    {'name': f'Item {num}', 'id': f'Item {num}',
        'type': 'numeric', 'format': score_fmt}
    for num in range(1, 9)
] + [
    {'name': 'mean_score', 'id': 'mean_score',
        'type': 'numeric', 'format': score_fmt},
    {'name': 'Invited', 'id': 'Invited', 'type': 'numeric'},
    {'name': 'Responses', 'id': 'Responses', 'type': 'numeric'},
    {'name': 'Response Rate', 'id': 'Response Rate',
        'type': 'numeric', 'format': score_fmt}
]

# Set hideable tag on the fly
for column in columns:
    column['hideable'] = True

categories = ['Clarity of Learning Outcomes', 'Clear Assessment', "Demonstrate Learning Outcomes", "Feedback and Learning Outcomes",
              "Resources and Learning Outcomes", "Activities and Learning Outcomes", "Engagement", "Satisfaction"]

# App body design here
app.layout = html.Div(style={'fontColor': 'blue'},id='main-screen', children=[

    html.Img(src=app.get_asset_url('logo.png')),
    dbc.Col([
        # Top row, explanation stuff imported from text_info
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2(children='Overview'),
                    html.P(what_is_this, id='main-screen-h2-1',
                           style={'fontSize': 16}),
                    html.Ul([html.Li([item], style={'fontSize': 16}) for item in categories
                             ])
                ])]),
            dbc.Col([usage])]),
        
        # Middle row, interactive datatable
        html.Div([
            html.Div([dash_table.DataTable(id='datatable-page',
                                           columns=columns,
                                           hidden_columns=[
                                               'code', 'Response Rate', 'Invited'],
                                           page_current=0,
                                           page_size=PAGE_SIZE,
                                           page_action="custom",
                                           filter_action='custom',
                                           filter_query='',
                                           sort_action='custom',
                                           sort_mode='multi',
                                           sort_by=[],
                                           style_data_conditional=construct_cell_color(),

                                           style_table={'overflowX': 'auto'},
                                           style_cell={
                                               'fontSize': 20, 'color': 'black'},
                                           export_format='xlsx',
                                           export_headers='display',
                                           merge_duplicate_headers=True
                                           )])
        ]),
        more_info
        ])

])

# Modify cells shown from various input types
@app.callback(
    Output('datatable-page', 'data'),
    Input('datatable-page', 'page_current'),
    Input('datatable-page', 'page_size'),
    Input('datatable-page', 'sort_by'),
    Input('datatable-page', 'filter_query'),
)
def update_table(page_current, page_size, sort_by, filter, data=setu):
    filtering_expressions=filter.split(' && ')
    dff=data

    if not filter:
        return pd.Series([])

    for filter_part in filtering_expressions:
        col_name, operator, filter_value=split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff=dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff=dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff=dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff=dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    page=page_current
    size=page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
