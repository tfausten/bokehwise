from collections import OrderedDict
import os

CAT_TO_SUBCAT = OrderedDict()
CAT_TO_SUBCAT['Rent & Utilities'] = [
    'Rent', 'Heat/gas', 'TV/Phone/Internet', 'Electricity', 'Water', 'Utilities - Other']
CAT_TO_SUBCAT['Food & Drink'] = [
    'Groceries', 'Food and drink - Other', 'Dining out']
CAT_TO_SUBCAT['Household Supplies'] = [
    'Household supplies', 'Furniture', 'Electronics', 'Home - Other']
CAT_TO_SUBCAT['Travel & Entertainment'] = ['Hotel', 'Plane', 'Transportation - Other', 'Taxi',
                                           'Entertainment - Other', 'Games', 'Movies', 'Music', 'Sports']
CAT_TO_SUBCAT['Other'] = [
    'General', 'Clothing', 'Life - Other', 'Gifts', 'Education', 'Insurance', ' ']

DATA_PATH_PATTERN = os.path.normpath('./data/*_export.csv')

# bokeh hatch patterns to use in bars
hatch_patterns = ['blank', 'dot', 'ring', 'horizontal_line',
                  'vertical_line', 'cross', 'horizontal_dash', 'vertical_dash']
