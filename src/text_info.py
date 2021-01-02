import dash_html_components as html
import dash_bootstrap_components as dbc
what_is_this = ''' SETool is a data visualization app that summarizes SETU data for each unit and presents the data in a visually helpful manner.
For reference, the 8 items correspond to the following properties:
'''

visualization = '''
For the items, they are colored by their ranking out of 5. Redder colors are closer to 1 and greener colors are closer to 5. You may also hide and show entries by clicking on the Toggle Columns button then tapping on a category you wish to show/hide.
'''
technical = '''
A write-up on the full process is yet to be done. Data with scraped using a modified BS4 script (credits to Jake Vandenberg for the original script). Following the extraction, the plotly and dash libraries were used to create an interactive 
datatable on an interactive website.
'''

usage_dp = [
    "The data appears blank initially. Don't panic! You've simply not given any filters. A very simple filter would be >=1 in the Level category.",
    "Numeric columns (e.g Items 1-8, mean score, Responses) can be filtered using inequalities in the Filter data section.",
    "To sort by highest/lowest, click on the up/down arrow within the header of each category.",
    "Text rows (unit code and semester) can be filtered using the word you want, typically the school name.",
    "If there are more than 50 results, you can navigate to the next page by scrolling to the bottom and clicking on the next page icon."
]
usage = html.Div(children = [
    html.H2(children='The Basics'),
    html.Ul([html.Li([item], style={'fontSize': 16}) for item in usage_dp
                             ]),
    html.H2(children='What the visualization is'),
    html.P(children=visualization,style={'fontSize': 16})
]

)

more_info = dbc.Row([
    dbc.Col([html.Div(children=[
        html.H2(children='Contact me'),
        html.P('Made by Sai Kumar Murali Krishnan',style={'fontSize': 16}),
        html.A(children='Github\n',href='https://github.com/Theorvolt',style={'fontSize': 16}),
        html.A(children='LinkedIn',href='https://www.linkedin.com/in/sai-kumar-murali-krishnan/',style={'fontSize': 16})
        ])]),
    dbc.Col([html.Div(children = [
    html.H2(children='Technical information'),
    html.P(children=technical,style={'fontSize': 16})])])
    ])




