'''
This file contains unimplemented visualizations initially intended to appear but were scraped.
'''

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=spider_inf[' MGF5630_CAULFIELD_ON-CAMPUS_ON_S1-01 '],
    theta=categories,
    fill='toself',
    name=' MGF5630_CAULFIELD_ON-CAMPUS_ON_S1-01 '
))


unit_options = [{'label': name, 'value': name} for name in setu["code"]]
spider_inf = {setu["code"][a]: [setu[f"Item {i}"][a]
                                for i in range(1, 9)] for a in range(len(setu))}

html.Div([
    html.H2(children='Individual unit information',
            id='main-screen-h2-3'),
    dcc.Dropdown(
        id='unit-select',
        options=unit_options[1:16],
        value=' MTH2140_CLAYTON_ON-CAMPUS_ON_S1-01 '
    ),
    html.Div([html.A("Handbook link", href='https://handbook.monash.edu/2020/units/MTH2140',
                        id='handbook-link', className="main_row"),
                html.P(children='Enrolments',
                        className='main_row', id='enrolment'),
                html.P(children='Responses',
                        className='main_row', id='responses'),
                dcc.Graph(
        id='radar-unit',
        figure=fig,
        className="main_row"
    )])], id='main-screen-div')


@app.callback(
    # radar-unit is the id (i.e cell) and figure is the modified field
    Output('radar-unit', 'figure'),
    Output('handbook-link', 'href'),
    Output('enrolment', 'children'),
    Output('responses', 'children'),
    Input('unit-select', 'value'))    # similar, except value from unit-select is our input)
def update_figure(unit, data=setu):
    fig = go.Figure()
    unit_code = unit.replace(' ', '').split("_")[0][0:7]
    row = data[data['code'] == unit]

    fig.add_trace(go.Scatterpolar(
        r=spider_inf[unit],
        theta=categories,
        fill='toself',
        name=unit
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=False
    )

    fig.update_layout(transition_duration=500)

    return (fig, f'https://handbook.monash.edu/2020/units/{unit_code}', 'Enrolments: '+str(row.iloc[0]['Invited']), 'Responses: ' + str(row.iloc[0]['Responses']))

'''
@app.callback(
    Output('main-screen', 'style'),
    Output('main-screen-div', 'style'),
    Output('main-screen-h2-3', 'style'),
    Input('daq-light-dark-theme', 'value')
)
def change_bg(dark_theme):
    if(dark_theme):
        return [{'background-color': '#303030', 'color': 'white'} for _ in [0]*3]
    else:
        return [{'background-color': 'white', 'color': 'black'} for _ in [0]*3]


@app.callback(
    Output("graph", "figure"),
    [Input("school_1", "value"),
     Input("school_2", "value")])
def display_color(school1, school2):
    if school1 == "All":
        data_set1 = setu['mean_score']
    else:
        data_set1 = setu[setu['school'] == school1]['mean_score']
    if school2 == "All":
        data_set2 = setu['mean_score']
    else:
        data_set2 = setu[setu['school'] == school2]['mean_score']

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=data_set1, name=school1,
                               xbins=dict(start=1, end=5, size=0.01)))
    fig.add_trace(go.Histogram(x=data_set2, name=school2,
                               xbins=dict(start=1, end=5, size=0.01)))
    fig.update_layout(barmode='stack')

    return fig
'''
'''
html.Div(
    [
        dcc.Graph(id="graph"),
        html.P("School 1"),
        dcc.Dropdown(
            id='school_1',
            options=[{'label': name, 'value': name} for name in setu['school'].unique(
            )]+[{'label': 'All', 'value': 'All'}],
            value='FIT'
        ),
        html.P("School 2"),
        dcc.Dropdown(
            id='school_2',
            options=[{'label': name, 'value': name} for name in setu['school'].unique(
            )]+[{'label': 'All', 'value': 'All'}],
            value='MTH'
        )
    ]
)'''