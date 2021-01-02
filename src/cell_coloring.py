from colorutils import Color, hsv_to_hex


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
                    'filter_query': '{mean_score} <= 2',
                    'column_id': 'mean_score'
                },
                'backgroundColor': '#FF0000',
                'color': 'black'
            }
        ]
        +
        [   # For all values within [2,5], normalize then color map
            {
                'if': {
                    'filter_query': '{{mean_score}} > {lower} && {{mean_score}} <= {upper}'.format(lower=color_step/20, upper=(color_step+1)/20),
                    'column_id': 'mean_score',
                },
                'backgroundColor': red_green_map(normalize(color_step/20))
            }
            for color_step in range(40, 100, 1)
        ]
        +
        [
            {
                'if': {
                    'filter_query': '{{Item {n}}} <= 2'.format(n=num),
                    'column_id': f'Item {num}',
                },
                'backgroundColor': '#FF0000',
                'color': 'black'
            }
            for num in range(1, 9)
        ]
        +
        flatten([
            [
                {
                    'if': {
                        'filter_query': '{{Item {n}}} > {lower} && {{Item {n}}} <= {upper}'.format(n=num, lower=color_step/20, upper=(color_step+1)/20),
                        'column_id': f'Item {num}',
                    },
                    'backgroundColor': red_green_map(normalize(color_step/20)),
                    'color': 'black'
                }
                for color_step in range(40, 100, 1)
            ]
            for num in range(1, 9)  # Iterate over all 9 items
        ])
    )
