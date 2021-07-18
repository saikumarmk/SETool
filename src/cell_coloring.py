from colorutils import Color, hsv_to_hex
'''
This file implements the color map generated for numeric items in the table. Currently, values from [2,5.001] map to [0,0.4]
which is then used as their hue value. 
TODO: Implement normalized coloring, distribution of scores seems roughly normal?
'''

def normalize(value: float, a: float = 2, b: float = 5.001, limit: float = 0.4) -> float:
    '''
    Utilises a min-max scaling technique to normalize a value.
    [a,b] forms the interval that the dataset lies in.
    limit is the upper bound of the interval that's being mapped to.
    '''
    # Maps onto the interval [0,limit].
    if a >= b:
        raise ValueError('a must be less than b')
    return limit*float(value-a)/(b-a)


def red_green_map(norm_val: float) -> str:
    '''
    Converts a normalized value to a hex color.
    '''
    return hsv_to_hex((norm_val*360, 1, 1))


def flatten(expr):
    '''
    Turns a list of lists into a single list.
    [[...],[..],[.]] -> [...,..,.]
    '''
    return [item for sublist in expr for item in sublist]


def construct_cell_color():
    '''
    Returns a comditional formatter for the datatable to color cells with.
    '''
    return (
        # Logic for mean_score, same as items
        [   # Hardcap all scores under 2 to be red
            {
                'if': {
                    'filter_query': '{agg_score} <= 2',
                    'column_id': 'agg_score'
                },
                'backgroundColor': '#FF0000',
                'color': 'black'
            }
        ]
        +
        [   # For all values within [2,5], normalize then color map
            {
                'if': {
                    'filter_query': '{{agg_score}} > {lower} && {{agg_score}} <= {upper}'.format(lower=color_step/20, upper=(color_step+1)/20),
                    'column_id': 'agg_score',
                },
                'backgroundColor': red_green_map(normalize(color_step/20))
            }
            for color_step in range(40, 100, 1)
        ]
        +
        [
            {
                'if': {
                    'filter_query': '{{I{n}}} < 1.0'.format(n=num),
                    'column_id': f'I{num}',
                },
                'backgroundColor': '#808080',
                'color': 'white'
            }
            for num in range(1, 14) 
        ]
        +
        [
            {
                'if': {
                    'filter_query': '{{I{n}}} <= 2 && {{I{n}}} >= 1'.format(n=num),
                    'column_id': f'I{num}',
                },
                'backgroundColor': '#FF0000',
                'color': 'black'
            }
            for num in range(1, 14) 
        ]
        +
        flatten([
            [
                {
                    'if': {
                        'filter_query': '{{I{n}}} > {lower} && {{I{n}}} <= {upper}'.format(n=num, lower=color_step/20, upper=(color_step+1)/20),
                        'column_id': f'I{num}',
                    },
                    'backgroundColor': red_green_map(normalize(color_step/20)),
                    'color': 'black'
                }
                for color_step in range(40, 100, 1)
            ]
            for num in range(1, 14) 
        ])
    )
