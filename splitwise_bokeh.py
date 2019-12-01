import utils
import data_preparation
from constants import CAT_TO_SUBCAT
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.palettes import Category20 as palette
from bokeh.core.properties import value
from bokeh.layouts import gridplot, row
from bokeh.models.formatters import DatetimeTickFormatter, NumeralTickFormatter
from bokeh.models.widgets import Panel, Tabs

if __name__ == '__main__':
    expenses = data_preparation.get_expenses_df()

    # monthly by category data
    monthly_data = expenses.groupby('Category').resample('BMS').sum()
    monthly_data = monthly_data.Cost.unstack(level=0)
    monthly_data = monthly_data.fillna(0)

    source = ColumnDataSource(monthly_data)
    col_names = CAT_TO_SUBCAT.keys()
    date_formatter = DatetimeTickFormatter(months=["%m/%y"])
    y_formatter = NumeralTickFormatter(format='0a')

    # TODO make color-selection more understandable
    colors = [palette[20][i] for i in [1, 5, 3, 7, 15]]
    print(colors)

    monthly_overview = figure(x_axis_label='Month', y_axis_label='Expenses',
                              x_axis_type='datetime', plot_height=500, plot_width=800,
                              tools="hover, tap", tooltips="$name: @$name")

    monthly_overview.vbar_stack(stackers=col_names, x='Date',
                                width=2e9, color=colors,
                                source=source, legend=[value(x) for x in col_names])
    monthly_overview.y_range.start = 0
    monthly_overview.yaxis.formatter = y_formatter
    legend = monthly_overview.legend[0]
    monthly_overview.add_layout(legend, 'right')

    ###################################################################################

    panels = []
    for i, col_name in enumerate(col_names):
        p = figure(x_axis_label='Month', y_axis_label='Expenses',
                   x_axis_type='datetime', tools="hover, tap",
                   tooltips=f"@Date{{%F}}: @{{{col_name}}}")
        p.vbar(x='Date', top=col_name, width=2e9,
               color=colors[i], source=source)
        p.xaxis.major_label_orientation = 0.8
        p.xaxis.formatter = date_formatter
        p.yaxis.formatter = y_formatter

        panels.append(Panel(child=p, title=col_name))

    # main_grid = gridplot(category_plots, ncols=3)
    main_tab = Panel(child=monthly_overview, title='Overview')
    panels.insert(0, main_tab)

    tabs = Tabs(tabs=panels)
    show(tabs)
