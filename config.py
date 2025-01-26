from pathlib import Path

WORKDIR_ROOT = Path.home().joinpath('.aitrader')
WORKDIR_ROOT = Path('D:/quant').joinpath('.aitrader')
#DATA_QUOTES = WORKDIR_ROOT.joinpath('quotes')
WORKDIR = Path(__file__).parent

DATA_DIR = WORKDIR.joinpath("data")
DATA_DIR_QUOTES = DATA_DIR.joinpath('quotes')
DATA_DIR_QUOTES_INDEX = DATA_DIR.joinpath('quotes_index')
dirs = [WORKDIR_ROOT, DATA_DIR, DATA_DIR_QUOTES, DATA_DIR_QUOTES_INDEX]

for dir in dirs:
    dir.mkdir(exist_ok=True, parents=True)

factors = [
    {'cat': '基础指标', 'id': 'base', 'inds': [
        {'name': '开盘价', 'show_name': '开盘价', 'expr': 'open'},
        {'name': '最高价', 'show_name': '最高价', 'expr': 'high'},
        {'name': '最低价', 'show_name': '最低价', 'expr': 'low'},
        {'name': '收盘价', 'show_name': '收盘价', 'expr': 'close'},
        {'name': '成交量', 'show_name': '成交量', 'expr': 'volume'},
        {'name': '动量', 'show_name': '动量(20)', 'expr': 'roc(close,20)'},
        {'name': '斜率', 'show_name': '斜率(25)', 'expr': 'slope(close,25)'},

    ]
     },
    {'cat': '技术指标', 'id': 'tech', 'inds':
        [
            {'name': 'RSRS', 'show_name': 'RSRS(18)', 'expr': 'RSRS(high,low,18)'},
            {'name': 'RSRS标准分', 'show_name': 'RSRS标准分(18,600)', 'expr': 'RSRS_zscore(high,low,18,600)'},
            {'name': '均线快慢线之差', 'show_name': '均线快慢线之差(5,20)', 'expr': 'ma(close,5)>ma(close,20)'},
            {'name': '收盘价与布林带上轨之差', 'show_name': '收盘价与布林带上轨之差(20,2)', 'expr': 'close>bbands_up(close,20,2)'},
            {'name': '收盘价与布林带下轨之差', 'show_name': '收盘价与布林带下轨之差(20,2)', 'expr': 'close<bbands_down(close,20,2)'},
            {'name': 'ATR', 'show_name': 'ATR(14)', 'expr': 'ta_atr(high,low,close,14)'},
        ]
     },
]


def get_all_factors():
    inds = {}
    for cat in factors:
        for ind in cat['inds']:
            inds[ind['name']] = ind
    return inds
