import utils
import data_preparation
from constants import CAT_TO_SUBCAT
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.palettes import Category20 as palette
from bokeh.core.properties import value
from bokeh.models import Legend
from bokeh.layouts import gridplot, row
from bokeh.models.formatters import DatetimeTickFormatter, NumeralTickFormatter

if __name__ == '__main__':
    expenses = data_preparation.get_expenses_df()

    # monthly by category data
    monthlyByCategory = expenses.groupby('Category').resample('BMS').sum()
    monthlyByCategoryUnstacked = monthlyByCategory.Cost.unstack(level=0)
    monthlyByCategoryUnstacked = monthlyByCategoryUnstacked.fillna(0)

    source = ColumnDataSource(monthlyByCategoryUnstacked)
    col_names = CAT_TO_SUBCAT.keys()
    # TODO make color-selection more understandable
    colors = [palette[20][i] for i in [1, 5, 3, 7, 15]]
    print(colors)

    monthlyBars = figure(x_axis_label='Month', y_axis_label='Expenses', x_axis_type='datetime',
                         plot_height=500, plot_width=800,
                         tools="hover", tooltips="$name: @$name")

    monthlyBars.vbar_stack(stackers=col_names, x='Date',
                           width=2e9, color=colors,
                           source=source, legend=[value(x) for x in col_names])

    monthlyBars.y_range.start = 0

    legend = monthlyBars.legend[0]
    # monthlyBars.legend[0].plot = None
    monthlyBars.add_layout(legend, 'right')


    dateFormatter = DatetimeTickFormatter(months=["%m/%y"])
    yFormatter = NumeralTickFormatter(format='0a')

    # plots = []
    # for i, col in enumerate(colNames):
    #     p = figure(title=col, x_axis_label=None, y_axis_label=None, x_axis_type='datetime',
    #                plot_height=200, plot_width=240,
    #                    tools="hover, tap",tooltips='cost: @Clothing')# tooltips=f'cost: @{{{col}}}')
    #     p.vbar(x='Date', top=col, width=2e9, color=colors[i], source=source)
    #     p.title.text_font_size = '8pt'
    #     p.xaxis.major_label_orientation = 0.8
    #     plots.append(p)
    #     p.xaxis.formatter = dateFormatter
    #     p.yaxis.formatter = yFormatter

    # grid1 = gridplot(plots, ncols=3)
    # show(row(monthlyBars, grid1))

    ################################################################################

    # make hover tool data by iterating over expenses df and adding to source data
    months_n = len(source.data['Date'])

    for category in expenses['Category'].unique():
        mask = expenses['Category'] == category
        categoryData = expenses[mask]

        monthlyEntries = pd.Series(index=source.data['Date'], data='')

        for i in range(len(categoryData)):
            description = categoryData.iloc[i]['Description']
            cost = categoryData.iloc[i]['Cost']
            entry = f'{description}: {cost}\n'

            year = categoryData.index[i].year
            month = categoryData.index[i].month
            date = f'{year}-{month}'

            monthlyEntries[date] += entry

        source.add(monthlyEntries.to_list(), f'{category}_entries')
        # print(source.data)

    ###################################################################################

    plots = []
    for i, col in enumerate(col_names):
        entries_field = f'{col}_entries'
        p = figure(title=col, x_axis_label=None, y_axis_label=None, x_axis_type='datetime',
                   plot_height=200, plot_width=240,
                   tools="hover, tap")
        p.vbar(x='Date', top=col, width=2e9, color=colors[i], source=source)
        p.title.text_font_size = '8pt'
        p.xaxis.major_label_orientation = 0.8
        plots.append(p)
        p.xaxis.formatter = dateFormatter
        p.yaxis.formatter = yFormatter

        p.add_tools(HoverTool(tooltips=f'@{{{entries_field}}}'))

    # tooltips = f'@{{{entries_field}}}'

    grid2 = gridplot(plots, ncols=3)

    # output
    show(row(monthlyBars, grid2))