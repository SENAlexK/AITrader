import backtrader as bt

cerebro = bt.Cerebro()

# 参数配置
cerebro.broker.setcash(100 * 1000)
# 滑点：双边各 0.0001
cerebro.broker.set_slippage_perc(perc=0.0001)
cerebro.addanalyzer(bt.analyzers.PyFolio,_name='pyfolio')

# 数据加载
import pandas as pd


def get_data(symbol):
    data = pd.read_csv('data/{}.csv'.format(symbol))
    data['date'] = data['date'].apply(lambda x: str(x))
    data.set_index('date', inplace=True)
    data.sort_index(ascending=True, inplace=True)
    data.index = pd.to_datetime(data.index)
    data['openinterest'] = 0
    data = data[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
    return data


for symbol in ['159915.SZ']:
    data = bt.feeds.PandasData(dataname=get_data(symbol), name=symbol)
    cerebro.adddata(data)


# 指标与策略实现
class MyStrategy(bt.Strategy):
    # 策略初始化
    def __init__(self):
        # 定义两个移动平均线指标，一个短期，一个长期
        self.roc = bt.indicators.ROC(period=20)
    # 策略逻辑
    def next(self):

        # 检查短期均线是否上穿长期均线
        if self.roc[0] > 0.08:
            # 如果是，则买入
            if not self.position:
                self.order_target_percent(self.data, 0.99)

        if self.roc[0] < 0:
            if self.position:
                self.close(self.data)

cerebro.addstrategy(MyStrategy)
results = cerebro.run()

# 分析策略运行结果
result = results[0]
pyfolio = result.analyzers.getbyname('pyfolio')
returns, positions, transactions, gross_lev = pyfolio.get_pf_items()
import empyrical
#returns.index = returns.index.tz_convert(None)
print('累计收益：', round(empyrical.cum_returns_final(returns), 3))
print('年化收益：', round(empyrical.annual_return(returns), 3))
print('最大回撤：', round(empyrical.max_drawdown(returns), 3))
print('夏普比', round(empyrical.sharpe_ratio(returns), 3))
print('卡玛比', round(empyrical.calmar_ratio(returns), 3))

# quantstats分析
import quantstats as qs
qs.reports.basic(returns)

# 可视化
cerebro.plot()