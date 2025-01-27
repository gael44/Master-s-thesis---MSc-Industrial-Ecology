# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 11:47:24 2024

@author: user
"""

import pandas as pd


def sorting(matrix):
    """
    Sorts the columns and rows of the matrix.

    Parameters:
    matrix (pd.DataFrame): The input DataFrame to be sorted.

    Returns:
    pd.DataFrame: Sorted DataFrame.
    """
    # Sorting of the columns
    if isinstance(matrix.columns, pd.MultiIndex) and len(matrix.columns.levels) == 2:  # Allows sorting for matrices like Y or A
        matrix = matrix.sort_index(axis=1, level=0)
    else:
        matrix = matrix.sort_index(axis=1)

    # Sorting of the rows
    if isinstance(matrix.index, pd.MultiIndex) and len(matrix.index.levels) == 2:  # Prevents sorting F's rows
        matrix = matrix.sort_index(axis=0, level=0)

    return matrix
