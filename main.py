import subprocess
import sys
import threading

import toga
from toga import Size
from toga.constants import COLUMN, ROW
from toga.style import Pack
from gui.window_config import WindowConfig

import config


# from strategies.turtle_strategy import TurtleStrategy


def button_handler(widget):
    print("你好")


def build(app):
    box = toga.Box()

    button = toga.Button("你好，toga", on_press=button_handler)
    button.style.padding = 10
    button.style.flex = 1
    box.add(button)

    return box


class MainApp(toga.App):
    def do_stuff(self, widget, **kwargs):
        self.textpanel.value += "Do stuff\n"

    def do_clear(self, widget, **kwargs):
        self.textpanel.value = ""

    def close_handler(self, widget, **kwargs):
        self.non_resize_window.close()

    def show_config(self, widget, **kwargs):
        WindowConfig().show()

    def startup(self):
        brutus_icon_256 = "gui/resources/brutus-256"
        cricket_icon_256 = "gui/resources/cricket-256"
        tiberius_icon_256 = "gui/resources/tiberius-256"
        datas = toga.Group("数据下载与管理")

        data_future = toga.Command(
            self.do_stuff,
            text="下载期货数据",
            tooltip="下载期货主连合约数据",
            icon=brutus_icon_256,
            group=datas,
        )
        # data_2 = toga.Command(
        #     self.do_clear,
        #     text="backtrader回测+实盘一体引擎",
        #     tooltip="智能回测",
        #     icon=cricket_icon_256,
        #     group=datas,
        # )

        tools = toga.Group("工具")
        config = toga.Command(
            self.show_config,
            text="配置",
            tooltip="显示系统设置窗口",
            icon=tiberius_icon_256,
            group=tools
        )

        # Set up main window
        self.main_window = toga.MainWindow()
        #self.app.commands.add(data_2, config)
        #self.app.main_window.toolbar.add(data_2, config)

        self.webview = toga.WebView(
            url="http://www.ailabx.com/mall",
            # on_webview_load=self.on_webview_load,
            style=Pack(flex=1),
        )

        webview_box = toga.Box(
            children=[
                # button_box,
                # self.label,
                self.webview,
            ],
            style=Pack(flex=1, direction=COLUMN),
        )

        streamlit_box = toga.Box(
            children=[
                toga.WebView(
                    url="http://localhost:8501/",
                    # on_webview_load=self.on_webview_load,
                    style=Pack(flex=1),
                )
            ],
            style=Pack(flex=1, direction=COLUMN),
        )

        container = toga.OptionContainer(
            content=[("星球社群官网_策略优选", webview_box), ("AI智能量化投研", streamlit_box)]
        )
        container.current_tab = 1
        self.main_window.content = container

        self.main_window.show()

    async def on_backtest(self, button):
        self.btn_bkt.enabled = False
        from datafeed.dataloader import CSVDataloader
        from backtrader_extends.engine import BacktraderEngine
        from backtrader_extends.performance import PerformanceUtils
        from gui.bokeh_utils import BokehUtils

        df = CSVDataloader.get_backtrader_df('000300.SH', start_date='20050101')
        df.dropna(inplace=True)
        print(df)
        e = BacktraderEngine(df, init_cash=100 * 100 * 10000.0)
        await e.async_run_strategy(TurtleStrategy)
        equity, _, _ = e.get_results('000300.SH')

        df_ratios, df_corr, df_years = PerformanceUtils().calc_equity(equity)
        print(df_ratios)

        BokehUtils().show(equity, df_ratios, df_years, df_corr)
        self.update_web_result()
        self.btn_bkt.enabled = True

    def update_web_result(self):
        file_path = config.DATA_DIR.joinpath('result.html')

        # 打开文件并读取内容
        if file_path.exists():
            with open(file_path.resolve(), 'r', encoding='utf-8') as file:
                html_content = file.read()
            self.web_result.set_content("http://ailabx.com", html_content)

    def backtest_box(self):
        label = toga.Label("请选择策略：")
        strategy = toga.Selection(items=["海龟策略", "三重滤网", "网格交易"])
        # Buttons
        btn_style = Pack(flex=1)
        btn_do_stuff = toga.Button("回测", on_press=self.do_stuff, style=btn_style)
        btn_clear = toga.Button("Clear", on_press=self.do_clear, style=btn_style)

        self.textpanel = toga.MultilineTextInput(
            readonly=False, style=Pack(flex=1), placeholder="Ready."
        )
        # outer_box = toga.Box(
        #     children=[btn_box, self.textpanel],
        #     style=Pack(flex=1, direction=COLUMN, padding=10),
        # )

        strategy_box = toga.Box(
            children=[label, strategy], style=Pack(direction=ROW, padding=10)
        )

        symbols = toga.Selection(items=["沪深300指数（510500.SS）", "纳指100（510300.SH）"])
        symbols_box = toga.Box(
            children=[toga.Label('请选择标的：'), symbols], style=Pack(direction=ROW, padding=10)
        )

        benchmark = toga.Selection(items=["沪深300指数（510500.SS）", "纳指100（510300.SH）"])
        benchmark_box = toga.Box(
            children=[toga.Label('比较基准：'), benchmark], style=Pack(direction=ROW, padding=10)
        )

        dt_from = toga.DateInput()
        dt_to = toga.DateInput()
        date_from_box = toga.Box(
            children=[toga.Label('开始日期：'), dt_from], style=Pack(direction=ROW, padding=10)
        )

        date_to_box = toga.Box(
            children=[toga.Label('结束日期：'), dt_to], style=Pack(direction=ROW, padding=10)
        )

        btn_bkt = toga.Button('开始回测', on_press=self.on_backtest)
        self.btn_bkt = btn_bkt
        btn_opt = toga.Button('参数调优')
        btn_box = toga.Box(
            children=[btn_bkt, btn_opt], style=Pack(direction=ROW, padding=10)
        )

        progress = toga.ProgressBar(max=100, value=33, style=Pack(padding=10))
        logs = toga.MultilineTextInput(style=Pack(flex=1))
        logs.value = "回测开始。\n开始加载数据。"

        left_container = toga.Box(
            children=[strategy_box, symbols_box, benchmark_box, date_from_box, date_to_box, btn_box, progress, logs],
            style=Pack(direction=COLUMN)
        )

        web_result = toga.WebView(
            # on_webview_load=self.on_webview_load,
            style=Pack(flex=1),
        )
        self.web_result = web_result
        self.update_web_result()

        right_container = toga.Box(
            children=[web_result],
            style=Pack(direction=COLUMN)
        )

        split = toga.SplitContainer(content=[(left_container, 2), (right_container, 3)])

        return split


def main():
    return MainApp("aitrader_v4.0_AI量化投资实验室", app_id='4.0', author="飞狐", home_page="http://www.ailabx.com")


def run_streamlit():
    # 启动 Streamlit
    import subprocess, os
    streamlit_file = os.path.join(os.path.dirname(__file__), 'gui', 'streamlit_main.py')
    print(streamlit_file)
    p_restart = subprocess.Popen(["streamlit", "run", streamlit_file])
    return p_restart

    # sys.argv = ["streamlit", "run", streamlit_file]
    # stcli.main()


if __name__ == "__main__":
    p_restart = run_streamlit()
    main().main_loop()
    p_restart.kill()
