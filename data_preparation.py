import glob
import pandas as pd
import datetime
import re
from constants import CAT_TO_SUBCAT, DATA_PATH_PATTERN


def get_expenses_df():
    expenses = read_newest_csv()
    expenses = clean_df(expenses)
    expenses = aggregate_categories(expenses)
    expenses = expenses.sort_values('Date', ascending=False)
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
    """ select columns, delete balance and payment rows, convert types as needed
    """
    columns_to_keep = ['Description', 'Category', 'Cost', 'Currency']
    cleaned = expenses.filter(columns_to_keep)
    cleaned = cleaned[cleaned['Category'] != 'Payment']
    cleaned = cleaned[cleaned['Description'] != 'Total balance']
    cleaned.Cost = pd.to_numeric(cleaned.Cost, errors='coerce')
    cleaned.Category = pd.Categorical(cleaned.Category)

    # TODO convert foreign currencies to JPY
    return cleaned


def aggregate_categories(expenses):
    """ Add a Category column with a reduces number of cateogories and rename original category-column
    to Subcategory.

    Params
    ----------------
    expenses: dataframe

    Returns
    ---------------
    expenses: dataframe
    """
    expenses = expenses.rename(columns={'Category': 'Subcategory'})
    all_subcats = expenses['Subcategory'].unique()

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

    # add new column to aggregated
    expenses['Category'] = expenses['Subcategory'].map(subcat_to_cat)
    return expenses


if __name__ == '__main__':
    # some tests for the utility functions

    expenses = read_newest_csv()
    print('Head of newest expense dataframe')
    print(expenses.head(), '\n')

    expenses = clean_df(expenses)
    print('cleaned expenses')
    print(expenses.head(), '\n')

    expenses = aggregate_categories(expenses)
    print('added aggregated category column)')
    print(expenses.head())
