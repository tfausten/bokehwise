import data_preparation
from bokeh.models import ColumnDataSource, TapTool, BooleanFilter, CDSView
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.palettes import Category20c
from bokeh.models.formatters import DatetimeTickFormatter, NumeralTickFormatter
from bokeh.models.widgets import Panel, Tabs, DataTable, TableColumn, DateFormatter
from bokeh.layouts import row
from bokeh.events import Tap
import itertools
import pandas as pd


def get_cycled_list(iterable, length):
    """ returns cycled list of fixed length
    """
    cycled = itertools.cycle(iterable)
    sliced = itertools.islice(cycled, 0, length)
    return list(sliced)


def MonthlyGraph():
    monthly_graph = figure(x_axis_label='Month', y_axis_label='Expenses',
                           x_axis_type='datetime', sizing_mode='stretch_both',
                           tools="hover, tap", tooltips="$name: @$name")

    monthly_graph.y_range.start = 0
    y_formatter = NumeralTickFormatter(format='0a')
    # date_formatter = DatetimeTickFormatter(months=["%m/%y"])
    monthly_graph.yaxis.formatter = y_formatter
    return monthly_graph


# get data and prepare monthly data by category
expenses_df = data_preparation.get_expenses_df()
monthly_category_df = expenses_df.groupby('Category').resample('BMS').sum()
monthly_category_df = monthly_category_df.Cost.unstack(level=0)
monthly_category_df = monthly_category_df.fillna(0)
monthly_category_source = ColumnDataSource(monthly_category_df)
col_names = monthly_category_df.columns.tolist()
print('\nMonthly data by category\n', monthly_category_df.head())

# TODO make color-selection more understandable
palette = Category20c[20]
main_color_idxs = [0, 4, 8, 12, 16]
category_colors = [palette[i+2] for i in main_color_idxs]
category_colors = get_cycled_list(category_colors, len(col_names))

# create monthly bars of stacked categories
monthly_overview = MonthlyGraph()
monthly_overview.vbar_stack(stackers=col_names, x='Date',
                            width=2e9, color=category_colors,
                            source=monthly_category_source, legend_label=col_names)


expenses_source = ColumnDataSource(expenses_df)


def get_expenses_table(selected_month=None, category=None):
    table_columns = [
        TableColumn(field='Date', title='Date', formatter=DateFormatter()),
        TableColumn(field='Description', title='Description'),
        TableColumn(field='Category', title='Category'),
        TableColumn(field='Subcategory', title='Subcategory'),
        TableColumn(field='Cost', title='Cost')
    ]

    # which month is currently selected? subset data according to selection
    if selected_month is None:
        month_filter = [True] * len(expenses_source.data['Date'])
    else:
        source_datetimes = pd.DatetimeIndex(expenses_source.data['Date'])
        month_filter = [
            date.month == selected_month for date in source_datetimes]
    month_filter = BooleanFilter(month_filter)

    # filter for current category
    if category is None:
        category_filter = [True] * len(expenses_source.data['Category'])
    else:
        category_filter = [
            cat == category for cat in expenses_source.data['Category']]
    category_filter = BooleanFilter(category_filter)

    view = CDSView(source=expenses_source,
                   filters=[month_filter, category_filter])

    return DataTable(source=expenses_source, columns=table_columns,
                     view=view, sizing_mode='stretch_both')


expenses_table = get_expenses_table()
overview_row = row([monthly_overview, expenses_table],
                   sizing_mode='stretch_both')
overview_panel = Panel(
    child=overview_row,
    title='Overview')


def bar_tap_callback(event):
    """ update the expenses table to show only entries of the selected month """
    # TODO when no bar is selected list index out of range
    selected = monthly_category_source.selected.indices[-1]
    selected_month = monthly_category_df.index[selected].month
    expenses_table = get_expenses_table(selected_month)
    overview_row.children[1] = expenses_table


monthly_overview.on_event(Tap, bar_tap_callback)
panels = [overview_panel]


# make single-category plots, and group the data by subcategories
main_color_idxs_cycled = itertools.cycle(main_color_idxs)
for i, category in enumerate(col_names):
    subcat_df = expenses_df[expenses_df['Category'] == category]
    monthly_subcat_df = subcat_df.groupby('Subcategory').resample('BMS').sum()
    monthly_subcat_df = monthly_subcat_df.Cost.unstack(level=0)
    monthly_subcat_df = monthly_subcat_df.fillna(0)
    monthly_subcat_source = ColumnDataSource(monthly_subcat_df)
    subcats = monthly_subcat_df.columns.tolist()

    color_idx = next(main_color_idxs_cycled)
    colors = palette[color_idx:color_idx+4]
    colors = get_cycled_list(colors, len(subcats))
    p = MonthlyGraph()
    p.vbar_stack(stackers=subcats, x='Date', width=2e9,
                 color=colors, line_color='white', source=monthly_subcat_source,
                 legend_label=subcats)
    expenses_table = get_expenses_table(category=category)

    subcat_row = row([p, expenses_table], sizing_mode='stretch_both')

    panel = Panel(
        child=subcat_row,
        title=category)

    def bar_tap_callback_subcat(event):
        """ update the expenses table to show only entries of the selected month """
        # TODO does not work for panels because monthly subcat source get overwritten
        # in each pass through the loop. source needs to be created as a list and then
        # referenced by index
        print(monthly_subcat_source.selected.indices)
        selected = monthly_subcat_source.selected.indices[-1]

        print(selected)
        selected_month = monthly_subcat_df.index[selected].month
        expenses_table = get_expenses_table(selected_month, category)
        subcat_row.children[1] = expenses_table
    p.on_event(Tap, bar_tap_callback_subcat)
    panels.append(panel)

tabs = Tabs(tabs=panels)
curdoc().title = 'Bokehwise'
curdoc().add_root(tabs)
