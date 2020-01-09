import numpy as np
import pandas as pd

# Clean up infs
def clean_nulls(s, fill=0, inverse=False, fill_2 =0):
    """
    Replaces any null or inf values with zeros or any user specific value for a series
    :param s: a pandas Series
    :param fill: either a value to fill by or a string representing a position to fill by (ex = "max")
    :param inverse: if inverse, s will equal 1/s
    """

    # If not a value, get the value
    if type(fill)==str:
        match_dict = {'max':s.max(), 'min':s.min(), 'med':s.mean()}
        fill = match_dict.get(fill)

    s = s.fillna(fill)

    if inverse:
        s= 1/s

    s = s.replace([np.inf, -np.inf], np.nan)

    # If not a value, get the value
    if (inverse and type(fill_2)==str):
        match_dict = {'max':s.max(), 'min':s.min(), 'med':s.mean()}
        fill = match_dict.get(fill)

    if inverse:
        s = s.fillna(fill_2)

    return s
