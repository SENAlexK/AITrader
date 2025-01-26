import bt

from bt_algos_extend import Task


def roc_20():
    t = Task()
    t.name = '动量轮动_20'
    # 排序
    t.order_by_signal = 'roc(close,20)'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（大宗商品）
        '513100.SH',  # 纳指100（美股科技）
        '510300.SH',  # 沪深300ETf
        '159915.SZ'  # 创业板ETF （A股成长）
    ]
    return t


def roc_20_RSRS():
    t = Task()
    t.name = '动量轮动_20_RSRS'
    # 排序
    t.select_sell = ['RSRS(high,low,18)<0.8']
    t.order_by_signal = 'roc(close,20)'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（大宗商品）
        '513100.SH',  # 纳指100（美股科技）
        '510300.SH',  # 沪深300ETf
        '159915.SZ'  # 创业板ETF （A股成长）
    ]
    return t


def kf_roc_20():
    t = Task()
    t.name = '卡曼滤波_动量轮动_20'
    # 排序
    t.order_by_signal = 'kf(roc(close,20))'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（大宗商品）
        '513100.SH',  # 纳指100（美股科技）
        '510300.SH',  # 沪深300ETf
        '159915.SZ'  # 创业板ETF （A股成长）
    ]
    return t


def slope_25():
    t = Task()
    t.name = '斜率轮动_25'
    # 排序
    t.order_by_signal = 'slope(close,25)'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（大宗商品）
        '513100.SH',  # 纳指100（美股科技）
        '510300.SH',  # 沪深300ETf
        '159915.SZ'  # 创业板ETF （A股成长）
    ]
    return t


def slope_25_picktime():
    t = Task()
    t.name = '斜率轮动_25_动量择时'
    # 排序
    t.select_sell = ['roc(close,20)<0']
    t.order_by_signal = 'slope(close,25)'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（大宗商品）
        '513100.SH',  # 纳指100（美股科技）
        '510300.SH',  # 沪深300ETf
        '159915.SZ'  # 创业板ETF （A股成长）
    ]
    return t


def slope_25_rsrs():
    t = Task()
    t.name = '斜率轮动_25_RSRS择时'
    # 排序
    t.select_sell = ['RSRS(high,low,18)<0.8']
    t.order_by_signal = 'slope(close,25)'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（大宗商品）
        '513100.SH',  # 纳指100（美股科技）
        '510300.SH',  # 沪深300ETf
        '159915.SZ'  # 创业板ETF （A股成长）
    ]
    return t


def kf_slope_25():
    t = Task()
    t.name = '卡曼滤波_斜率轮动_25'
    # 排序
    t.order_by_signal = 'kf(slope(close,25))'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（大宗商品）
        '513100.SH',  # 纳指100（美股科技）
        '510300.SH',  # 沪深300ETf
        '159915.SZ'  # 创业板ETF （A股成长）
    ]
    return t


def kf2_slope_25():
    t = Task()
    t.name = '卡曼滤波2_斜率轮动_25'
    # 排序
    t.order_by_signal = 'kf2(slope(close,25))'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（大宗商品）
        '513100.SH',  # 纳指100（美股科技）
        '510300.SH',  # 沪深300ETf
        '159915.SZ'  # 创业板ETF （A股成长）
    ]
    return t


def etfs_roc_20():
    t = Task()
    t.name = '多ETF趋势轮动策略，均线+动量择时'
    # 排序
    t.start_date = '20200101'
    t.select_buy = [
        'roc(close,20)>0.05',
        'ma(close,5)>ma(close,20)']
    t.select_sell = [
        'roc(close, 20) > 0.2',
        'ma(close, 5) < ma(close, 20)'
    ]
    t.order_by_signal = 'roc(close,20)'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（大宗商品）
        '513100.SH',  # 纳指100（美股科技）
        '510300.SH',  # 沪深300ETf
        '159915.SZ'  # 创业板ETF （A股成长）
    ]
    return t


def risk_parity():
    t = Task()
    t.name = '大类资产配置-风险平价系列'
    # 排序
    t.start_date = '20200101'
    t.period = 'RunMonthly'  # 月底调仓
    t.weight = 'WeighSpecified'
    t.weight_fixed = {'510300.SH': 0.3, '511260.SH': 0.55, '159934.SZ': 0.075, '159985.SZ': 0.075}

    t.symbols = [
        '159934.SZ',  # 黄金ETF（黄金）
        '511260.SH',  # 十年国债ETF（债券）
        '510300.SH',  # 沪深300ETF（股票）
        '159985.SZ'  # 豆粕（商品）
    ]
    return t


def risk_parity_WeighEqually():
    t = Task()
    t.name = '大类资产配置-风险平价系列-25%权重'
    # 排序
    t.start_date = '20200101'
    t.period = 'RunMonthly'  # 月底调仓
    t.weight = 'WeighEqually'
    # t.weight_fixed = {'510300.SH': 0.3, '511260.SH': 0.55, '159934.SZ': 0.075, '159985.SZ': 0.075}

    t.symbols = [
        '159934.SZ',  # 黄金ETF（黄金）
        '511260.SH',  # 十年国债ETF（债券）
        '510300.SH',  # 沪深300ETF（股票）
        '159985.SZ'  # 豆粕（商品）
        '513100.SH'  # 纳指100
        # '513100.SH'  # 纳指100
    ]
    return t


def risk_parity_hongli():
    t = Task()
    t.name = '大类资产配置-风险平价系列-等权重-红利低波'
    # 排序
    t.start_date = '20200101'
    t.period = 'RunMonthly'  # 月底调仓
    t.weight = 'WeighEqually'

    t.symbols = [
        '159934.SZ',  # 黄金ETF（黄金）
        '511260.SH',  # 十年国债ETF（债券）
        '512890.SH',  # 红利低波（股票）
        '159985.SZ',  # 豆粕（商品）
        # '513100.SH'  # 纳指100
    ]
    t.benchmark = '510300.SH'
    return t


def risk_parity_hongli_ndx():
    t = Task()
    t.name = '大类资产配置-风险平价系列-等权重-红利低波-纳指'
    # 排序
    t.start_date = '20200101'
    t.period = 'RunMonthly'  # 月底调仓
    t.weight = 'WeighEqually'

    t.symbols = [
        '159934.SZ',  # 黄金ETF（黄金）
        '511260.SH',  # 十年国债ETF（债券）
        '512890.SH',  # 红利低波（股票）
        '159985.SZ',  # 豆粕（商品）
        '513100.SH'  # 纳指100
    ]
    t.benchmark = '510300.SH'
    return t


def astock_rolling():
    t = Task()
    t.name = '大小盘轮动'
    # 排序
    t.start_date = '20200101'
    # t.period = 'RunMonthly'  # 月底调仓
    t.weight = 'WeighEqually'

    t.symbols = [
        '512890.SH'  # 创业板
    ]
    t.benchmark = '512890.SH'
    t.select_buy = ['roc(close,20)>0.08']
    t.select_sell = ['roc(close,20)<0']
    t.order_by_signal = 'roc(close,20)'
    return t


def portfolio_rolling():
    t = Task()
    t.name = '组合轮动'
    t.symbols = [
        '159934.SZ',  # 黄金ETF（黄金）
        # '511260.SH',  # 十年国债ETF（债券）
        # '161716.SZ',
        '512890.SH',  # 红利低波（股票）
        '159985.SZ',  # 豆粕（商品）
        '513100.SH'  # 纳指100
    ]
    t.period = 'RunWeekly'
    # t.order_by_signal = 'roc(close,20)'
    t.order_by_signal = 'ts_corr(close, high, 5)'
    t.order_by_signal = 'ts_argmaxmin(low+close, 5)'
    # t.order_by_signal = 'ts_argmin(close, 60)*ts_rank(sqrt(volume), 5)'
    t.order_by_signal = 'ts_pct_change(ts_maxmin(close, 60), 5)'
    return t


def task_list():
    tasks = [portfolio_rolling(), roc_20(), slope_25(), slope_25_picktime(), slope_25_rsrs(), kf_slope_25(),
             kf2_slope_25(), kf_roc_20(),
             roc_20_RSRS(), etfs_roc_20(), risk_parity(), risk_parity_WeighEqually(), risk_parity_hongli(),
             risk_parity_hongli_ndx()]
    return tasks
