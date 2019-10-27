import glob
import pandas as pd
import datetime
import os
import re
from constants import CAT_TO_SUBCAT, DATA_PATH_PATTERN

def get_expenses_df():
    expenses = read_newest_csv()
    expenses = clean_df(expenses)
    expenses = aggregate_categories(expenses)
    print('cleaned and preprocessed data:')
    print(expenses.head())

    return expenses

def read_newest_csv():
    """ Returns the newest splitwise-exported csv data as a dataframe,
    assuming the splitwise date pattern in csv-filenames
    """
    file_paths = glob.glob(DATA_PATH_PATTERN)

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


def aggregate_categories(expenses):
    """ Reduces the number of categories in the expenses df, by aggregating
    into main categories.

    Params
    ----------------
    expenses: dataframe

    Returns
    ---------------
    aggregated: dataframe
    """
    aggregated = expenses.rename(columns={'Category': 'Subcategory'})
    all_subcats = aggregated['Subcategory'].unique()

    # check wether all expense categories are present in aggregation_dict
    flattened_dict_cats = [cat for subcat_list in
                           [v for k, v in CAT_TO_SUBCAT.items()] for cat in subcat_list]
    cat_difference = set(all_subcats).difference(set(flattened_dict_cats))

    if len(cat_difference) > 0:
        raise ValueError(
            f'The following categories appear in the data, but are not represented in the category aggregation dict: {cat_difference}'
        )

    # invert the category_to_subcategory dict
    subcat_to_cat = {}
    for cat, subcat_list in CAT_TO_SUBCAT.items():
        subcat_to_cat.update({subcat: cat for subcat in subcat_list})

    print(subcat_to_cat)

    # add new column to aggregated
    aggregated['Category'] = aggregated['Subcategory'].map(subcat_to_cat)
    return aggregated


if __name__ == '__main__':
    # some tests for the utility functions

    expenses = read_newest_csv()
    print('Head of newest expense dataframe')
    print(expenses.head(), '\n')

    expenses = clean_df(expenses)
    print('cleaned expenses')
    print(expenses.tail(), '\n')

    expenses = aggregate_categories(expenses)
    print(expenses.head())
