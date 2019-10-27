import glob
import pandas as pd
import datetime
import os
import re


def colors_from_palette(palette, n_colors):
    """
    Params
    ----------------
    palette: dict, bokeh palette with the number of colors as keys
    n_colors: int, number of colors to return

    Returns
    ------------
    colors: list,
        list of colors of length n_colors.
        If n_colors > len(palette) the same color appear multiple times.
    """
    max_palette_colors = max(palette.keys())
    min_palette_colors = min(palette.keys())

    if n_colors < min_palette_colors:
        colors = palette[min_palette_colors]
        colors = colors[:n_colors]

    elif n_colors <= max_palette_colors:
        colors = palette[n_colors]

    else:   # the case that n_colors > max_palette_colors
        palette_colors = palette[max_palette_colors]
        indices = range(0, n_colors)
        indices = [i - (i // len(palette_colors)) *
                   len(palette_colors) for i in indices]
        colors = [palette_colors[i] for i in indices]

    return colors


if __name__ == '__main__':
    # some tests for the utility functions
    from bokeh.palettes import Category20

    n_colors = 30
    print(f'Choosing {n_colors} colors from palette Category20')
    colors = colors_from_palette(Category20, n_colors)
    print(colors, '\n')
    assert n_colors == len(colors)
