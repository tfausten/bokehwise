import data_preparation
from constants import CAT_TO_SUBCAT
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.palettes import Category20c
from bokeh.models.formatters import DatetimeTickFormatter, NumeralTickFormatter
from bokeh.models.widgets import Panel, Tabs, DataTable, TableColumn, DateFormatter
from bokeh.layouts import row
import itertools

expenses = data_preparation.get_expenses_df()

# monthly by category data
category_data = expenses.groupby('Category').resample('BMS').sum()
category_data = category_data.Cost.unstack(level=0)
category_data = category_data.fillna(0)
print('\nmonthly_data\n', category_data.head())

category_source = ColumnDataSource(category_data)
col_names = [str(n) for n in CAT_TO_SUBCAT.keys()]
date_formatter = DatetimeTickFormatter(months=["%m/%y"])
y_formatter = NumeralTickFormatter(format='0a')


def get_cycled_list(iterable, length):
    """ returns cycled list of fixed length
    """
    cycled = itertools.cycle(iterable)
    sliced = itertools.islice(cycled, 0, length)
    return list(sliced)


# TODO make color-selection more understandable
palette = Category20c[20]
main_color_idxs = [0, 4, 8, 12, 16]
category_colors = [palette[i+2] for i in main_color_idxs]
category_colors = get_cycled_list(category_colors, len(col_names))


def create_default_fig():
    fig = figure(x_axis_label='Month', y_axis_label='Expenses',
                 x_axis_type='datetime', sizing_mode='stretch_both',
                 tools="hover, tap", tooltips="$name: @$name")
    fig.y_range.start = 0
    fig.yaxis.formatter = y_formatter
    return fig


monthly_overview = create_default_fig()
monthly_overview.vbar_stack(stackers=col_names, x='Date',
                            width=2e9, color=category_colors,
                            source=category_source, legend_label=col_names)

# add expense table
expenses = expenses.sort_values('Date', ascending=False)
expenses_source = ColumnDataSource(expenses)
expenses_columns = [
    TableColumn(field='Date', title='Date', formatter=DateFormatter()),
    TableColumn(field='Description', title='Description'),
    TableColumn(field='Category', title='Category'),
    TableColumn(field='Cost', title='Cost')
]
overview_table = DataTable(source=expenses_source, columns=expenses_columns)

overview_panel = Panel(
    child=row([monthly_overview, overview_table], sizing_mode='stretch_both'),
    title='Overview')

panels = []
panels.append(overview_panel)


# make single-category plots, and group the data by subcategories
main_color_idxs_cycled = itertools.cycle(main_color_idxs)
for i, col_name in enumerate(col_names):
    subcat_data = expenses[expenses['Category'] == col_name]
    subcat_data = subcat_data.groupby('Subcategory').resample('BMS').sum()
    subcat_data = subcat_data.Cost.unstack(level=0)
    subcat_data = subcat_data.fillna(0)
    # print('\nmonthly_data\n', subcat_data.head())
    subcat_source = ColumnDataSource(subcat_data)
    subcats = subcat_data.columns.tolist()

    color_idx = next(main_color_idxs_cycled)
    print(color_idx)
    colors = palette[color_idx:color_idx+4]
    colors = get_cycled_list(colors, len(subcats))

    p = create_default_fig()
    p.vbar_stack(stackers=subcats, x='Date', width=2e9,
                 color=colors, line_color='white', source=subcat_source,
                 legend_label=subcats)

    panels.append(Panel(child=p, title=col_name))

tabs = Tabs(tabs=panels)
curdoc().title = 'Bokehwise'
curdoc().add_root(tabs)
