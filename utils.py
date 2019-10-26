import glob
import pandas as pd
import datetime
import os
import re


def read_newest_csv():
    """ Returns the newest splitwise-exported csv data as a dataframe,
    assuming the splitwise date pattern in csv-filenames
    """
    data_dir = './data'
    filepath_pattern = os.path.join(data_dir + '/*_export.csv')
    file_paths = glob.glob(filepath_pattern)

    date_pattern = r'\d{4}-\d{2}-\d{2}'
    dates = [re.search(date_pattern, path).group() for path in file_paths]

    datetime_pattern = "%Y-%m-%d"
    datetimes = [datetime.datetime.strptime(
        date, datetime_pattern) for date in dates]

    newest_file_index = datetimes.index(max(datetimes))
    newest_file_path = file_paths[newest_file_index]

    expenses = pd.read_csv(
        newest_file_path, index_col='Date', parse_dates=True)
    print("Read Splitwise data from ", newest_file_path)
    return expenses


def clean_df(expenses):
    columns_to_keep = ['Description', 'Category', 'Cost', 'Currency']
    cleaned = expenses[columns_to_keep].iloc[:-1]  # remove total balance row
    cleaned = cleaned[cleaned['Category'] != 'Payment']
    cleaned.Cost = pd.to_numeric(cleaned.Cost)
    cleaned.Category = pd.Categorical(cleaned.Category)
    return cleaned


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

    expenses = read_newest_csv()
    print('Head of newest expense dataframe')
    print(expenses.head(), '\n')

    expenses = clean_df(expenses)
    print('cleaned expenses')
    print(expenses.tail(), '\n')

    n_colors = 30
    print(f'Choosing {n_colors} colors from palette Category20')
    colors = colors_from_palette(Category20, n_colors)
    print(colors, '\n')
    assert n_colors == len(colors)
