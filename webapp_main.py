import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from src.cell_coloring import construct_cell_color
from dash.dependencies import Input, Output, State
from dash_table.Format import Format, Scheme, Symbol, Group
import dash_table
import dash_bootstrap_components as dbc
from src.table_filter import split_filter_part
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import os
from src.text_info import what_is_this, usage, more_info

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
# Meta tags help mobile render
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,    meta_tags=[
                {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}])
server = app.server


PAGE_SIZE = 50

# Initializing df and adding a few new columns
setu = pd.read_csv("assets/SETU_ALL_2020.csv").drop(columns=["Unnamed: 0"])
comparison = pd.Series([], dtype=object)
setu['id'] = range(len(setu))
setu['Handbook'] = '[Link](https://handbook.monash.edu/2021/units/' + \
    setu.unit_code+')'
setu.set_index('id', inplace=True, drop=False)

# Then set up headers for the datatable
score_fmt = Format().scheme(Scheme.fixed).precision(2)
columns = [
    {'name': 'code', 'id': 'code'},
    {'name': 'Unit Code', 'id': 'unit_code'},
    {'name': 'Level', 'id': 'Level', 'type': 'numeric'}, # TODO remove season
    {'name': 'Season', 'id': 'Semester'}, # TODO CHANGE TO Season WHAT THE FUCK DID YOU DO HERE ???
] + [
    {'name': f'I{num}', 'id': f'I{num}',
        'type': 'numeric', 'format': score_fmt}
    for num in range(1, 9) # TODO CHANGE TO 14
] + [
    {'name': 'mean_score', 'id': 'mean_score',
        'type': 'numeric', 'format': score_fmt},
    {'name': 'Invited', 'id': 'Invited', 'type': 'numeric'},
    {'name': 'Responses', 'id': 'Responses', 'type': 'numeric'},
    {'name': 'Response Rate', 'id': 'Response Rate',
        'type': 'numeric', 'format': score_fmt},
    {
        'name': 'Handbook', 'id': 'Handbook', 'presentation': 'markdown'
    }
]

# Set hideable tag on the fly
for column in columns:
    column['hideable'] = True

# TODO: Put all text in text_info
categories = [
    'Clarity of Learning Outcomes', 'Clear Assessment', 
"Demonstrate Learning Outcomes", "Feedback and Learning Outcomes",
"Resources and Learning Outcomes", "Activities and Learning Outcomes", 
"Engagement", "Satisfaction", # Need to add in the 12 items
"Relevant assessment to unit", "Links between content",
"Good mix of theory and app.", "Active participation",
"Capacity for critical thinking"

]

# App body design here
app.layout = html.Div(style={'fontColor': 'blue'}, id='main-screen', children=[

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
        # Filter table
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2(children='Filters'),
                    html.H3(children='Show Levels'),
                    dcc.Checklist(id='levels', options=[
                                  {'label': num, 'value': num} for num in range(1, 10)], value=[], labelStyle={'fontSize': 16, 'textAlign': 'right', 'padding-left': '5px'}),
                    html.H3(children='Hide flexible variants?'),
                    dcc.Checklist(id='flexible', options=[
                                  {'label': "", 'value': 'Yes'}], value=[], labelStyle={'fontSize': 16, 'textAlign': 'right', 'padding-left': '5px'}),
                    html.H3(children='Show Semester'),
                    dcc.Checklist(id='semester', options=[{'label': "S1", 'value': 'S1'}, {'label': "S2", 'value': 'S2'}], value=[
                    ], labelStyle={'fontSize': 16, 'textAlign': 'right', 'padding-left': '5px'}),
                    dcc.RadioItems(options=[
                    {'label':'Mean', 'value':0},
                    {'label':'Median','value':1}],
                    id='meanmedian',
                    value=0,
                    labelStyle={'fontSize': 16, 'textAlign': 'right', 'padding-left': '5px'})
                ])
            ])
        ]),

        # Middle row, interactive datatable
        html.Div([
            html.Div([dash_table.DataTable(id='datatable-page',
                                           columns=columns,
                                           hidden_columns=[
                                               'Level','Handbook','code', 'Response Rate', 'Invited'],
                                           page_current=0,
                                           page_size=PAGE_SIZE,
                                           page_action="custom",
                                           filter_action='custom',
                                           filter_query='',
                                           sort_action='custom',
                                           sort_mode='multi',
                                           row_selectable='multi',
                                           tooltip_delay=0,
                                           tooltip_duration=None,
                                           tooltip_header={
                                               f'I{num+1}': categories[num] for num in range(0, 8)}, # TODO add in items 1-9 & thing
                                           selected_rows=[],
                                           sort_by=[],
                                           style_data_conditional=construct_cell_color(),
                                           style_filter={
                                               'fontSize': 20, 'color': 'black', 'textAlign': 'center'},
                                           style_table={'overflowX': 'auto'},
                                           style_cell={
                                               'fontSize': 20, 'color': 'black', 'textAlign': 'center'},
                                           merge_duplicate_headers=True
                                           )])
        ], style={'padding-top': '25px', 'padding-bottom': '25px'}),
        dbc.Row(html.Div(children=[html.H2(children='Comparison Table')])),
        # Comparison table
        html.Div([
            html.Div([dash_table.DataTable(id='compare-table',
                                           data=comparison,
                                           columns=columns,
                                           hidden_columns=[
                                               'Level','Handbook','code', 'Response Rate', 'Invited'],
                                           page_current=0,
                                           page_size=PAGE_SIZE,
                                           page_action="custom",
                                           filter_action='custom',
                                           filter_query='',
                                           sort_action='custom',
                                           sort_mode='multi',
                                           sort_by=[],
                                           editable=True,
                                           row_deletable=True,
                                           style_data_conditional=construct_cell_color(),
                                           tooltip_delay=0,
                                           tooltip_duration=None,
                                           tooltip_header={
                                               f'I{num+1}': categories[num] for num in range(0, 8)}, # TODO FUUUUUUUUCK
                                           style_table={'overflowX': 'auto'},
                                           style_cell={
                                               'fontSize': 20, 'color': 'black', 'textAlign': 'center'},
                                           style_filter={
                                               'fontSize': 20, 'color': 'black', 'textAlign': 'center'},
                                           merge_duplicate_headers=True
                                           )])
        ], style={'padding-top': '50px'}),
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
    Input('flexible', 'value'),
    Input('levels', 'value'),
    Input('semester', 'value'),
    Input('meanmedian','value')
)
def update_table(page_current, page_size, sort_by, filter, flexible, levels, semester, meanmedian, data=setu):
    '''
    Need a way to switch between median and mean


    '''

    filtering_expressions = filter.split(' && ')
    dff = data

    # No input, don't show anything
    if not filter:
        return pd.Series([], dtype=object)

    if flexible:  # i.e non empty list
        dff = dff.loc[dff['code'].str.contains('CAMPUS')]

    if levels:  # something was chosen
        dff = dff.loc[dff['Level'].isin(levels)]

    if semester:  # TODO sem was chosen, this will be replaced with season, do .str.contains any of
        dff = dff.loc[dff['Semester'].isin(semester)]

    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    # At the very end, get by mean or median, 0 = mean, median = 1
    '''
    dff[[f'I{n}' for n in range(1,9)]] = dff[[f'I{n}' for n in range(1,9)]].apply(lambda x:x[meanmedian])
    Also change agg score if needed
    '''

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    page = page_current
    size = page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')

# modify comparison table


@app.callback(
    Output('compare-table', 'data'),
    Input('compare-table', 'page_current'),
    Input('compare-table', 'page_size'),
    Input('compare-table', 'sort_by'),
    Input('compare-table', 'filter_query'),
    Input('datatable-page', 'derived_virtual_data'),
    Input('datatable-page', 'selected_row_ids'),
    Input('meanmedian','value'),
    State('compare-table', 'data')
)
def update_comparison(page_current, page_size, sort_by, filter, rows, dv_rows, meanmedian, data):
    filtering_expressions = filter.split(' && ')
    if dv_rows:
        data = pd.concat([pd.DataFrame(data), setu.iloc[dv_rows]]
                        ).drop_duplicates()
    dff = pd.DataFrame(data)
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    page = page_current
    size = page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')


if __name__ == '__main__':
    #
    app.run_server(debug=False, port=int(
        os.environ.get('PORT', 5000)),host='0.0.0.0')
