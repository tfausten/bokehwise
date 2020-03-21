import data_preparation
from constants import CAT_TO_SUBCAT
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.palettes import Category20 as palette
from bokeh.models.formatters import DatetimeTickFormatter, NumeralTickFormatter
from bokeh.models.widgets import Panel, Tabs

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

# TODO make color-selection more understandable
# use cycle for the color palette
colors = [palette[20][i] for i in [1, 5, 3, 7, 15]]
print(colors)


def create_default_fig():
    fig = figure(x_axis_label='Month', y_axis_label='Expenses',
                 x_axis_type='datetime', sizing_mode='stretch_both',
                 tools="hover, tap", tooltips="$name: @$name")
    fig.y_range.start = 0
    fig.yaxis.formatter = y_formatter
    return fig


monthly_overview = create_default_fig()
monthly_overview.vbar_stack(stackers=col_names, x='Date',
                            width=2e9, color=colors,
                            source=category_source, legend_label=col_names)

panels = []
panels.append(Panel(child=monthly_overview, title='Overview'))


# make single-category plots, and group the data by subcategories
for i, col_name in enumerate(col_names):
    subcat_data = expenses[expenses['Category'] == col_name]
    subcat_data = subcat_data.groupby('Subcategory').resample('BMS').sum()
    subcat_data = subcat_data.Cost.unstack(level=0)
    subcat_data = subcat_data.fillna(0)
    # print('\nmonthly_data\n', subcat_data.head())
    subcat_source = ColumnDataSource(subcat_data)
    subcats = subcat_data.columns.tolist()

    p = create_default_fig()
    p.vbar_stack(stackers=subcats, x='Date', width=2e9,
                 color=colors[i], line_color='black', source=subcat_source,
                 legend_label=subcats)

    panels.append(Panel(child=p, title=col_name))

tabs = Tabs(tabs=panels)
curdoc().title = 'Bokehwise'
curdoc().add_root(tabs)
