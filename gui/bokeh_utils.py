from bokeh.io import output_file, show
from bokeh.layouts import gridplot
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, save
from bokeh.transform import dodge

import config


class BokehUtils:
    def __init__(self):
        pass
        # pandas_bokeh.output_file(DATA_DIR_BKT_RESULT.joinpath('bkt_result.html'))

    def add_table(self, df_ratio, height=300):
        print(df_ratio)
        data_table = DataTable(
            columns=[TableColumn(field=Ci, title=Ci) for Ci in df_ratio.columns],
            source=ColumnDataSource(df_ratio),
            height=height,
        )
        return data_table

    def add_equity(self, df, title='时间序列'):
        # print(df)
        p = figure(width=800, height=600, title="净值曲线", x_axis_label='Date', y_axis_label='Value')

        # 绘制 'equity' 列
        p.line(df.index, df['return'], legend_label='策略', line_width=2, color='blue')

        # 绘制 'benchmark' 列
        p.line(df.index, df['000300.SH'], legend_label='基准', line_width=2, color='red')
        # p = df_equity.plot_bokeh(rangetool=True, show_figure=False, )
        p.legend.location = "top_left"
        return p

    def add_yearly(self, df):
        # print(df)
        df = df.T
        # fruits = df.columns
        years = list(df.index)

        data = {col: list(df[col]) for col in df.columns}
        data.update({'years': years})

        print(data)

        # data = {'fruits': df.index,
        #         '2015': [2, 1, 4, 3, 2, 4],
        #         '2016': [5, 3, 3, 2, 4, 6],
        #         '2017': [3, 2, 4, 4, 5, 3]}

        source = ColumnDataSource(data=data)

        p = figure(x_range=list(df.index), y_range=(-1, 1), title="按年收益率对比",
                   height=350, toolbar_location=None, tools="")

        p.vbar(x=dodge('years', -0.25, range=p.x_range), top='return', source=source,
               width=0.2, color="#ff0000", legend_label="策略")

        p.vbar(x=dodge('years', 0.0, range=p.x_range), top='000300.SH', source=source,
               width=0.2, color="#718dbf", legend_label="基准")

        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"

        return p

    def show(self, df_equity, df_ratio, df_yearly, df_corr):
        output_file(filename=config.DATA_DIR.joinpath('result.html').resolve(), title="策略回测")
        # grid = gridplot([[self.add_equity(df_equity), self.add_yearly(df_yearly)],
        #                  [, self.add_table(df_corr)],
        #                  ], sizing_mode='stretch_both')
        p1 = self.add_equity(df_equity)
        p2 = self.add_yearly(df_yearly)
        p3 = self.add_table(df_ratio)
        p4 = self.add_table(df_corr)
        p = gridplot([[p1, p2], [p3, p4]], sizing_mode='stretch_both')
        save(p)

        # import pandas_bokeh
        # p = pandas_bokeh.plot_grid([[self.add_equity(df_equity), self.add_yearly(df_yearly)],
        #                         [self.add_table(df_ratio), self.add_table(df_corr)],
        #                         ],show_plot=False
        #                        )

    # save(grid)
