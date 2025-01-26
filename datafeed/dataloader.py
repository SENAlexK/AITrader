import pandas as pd
from tqdm import tqdm

from config import DATA_DIR_QUOTES, DATA_DIR
from loguru import logger
from datetime import datetime

from datafeed.expr import calc_expr


class CSVDataloader:
    def __init__(self):
        pass

    @staticmethod
    def get_backtrader_df(symbol: str, start_date='20050101', end_date=datetime.now().strftime('%Y%m%d'),
                          path='quotes'):
        df = CSVDataloader.get_df([symbol], start_date=start_date, path=path)
        df.set_index('date', inplace=True)
        df['openinterest'] = 0
        df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
        df = df[df.index >= start_date]
        df = df[df.index <= end_date]

        return df

    @staticmethod
    def read_csv(symbol, path='quotes'):
        csv = DATA_DIR.joinpath(path).joinpath('{}.csv'.format(symbol))
        if not csv.exists():
            logger.warning('{}不存在'.format(csv.resolve()))
            return None

        df = pd.read_csv(csv.resolve(), index_col=None)
        df['date'] = df['date'].apply(lambda x: str(x))
        df['date'] = pd.to_datetime(df['date'])

        df['symbol'] = symbol
        df.dropna(inplace=True)
        return df

    @staticmethod
    def get_df(symbols: list[str] = None, set_index=False, start_date='20100101',
               end_date=datetime.now().strftime('%Y%m%d'), path='quotes'):
        dfs = []
        if symbols is None:
            # 获取所有当前目录下的csv列表
            import os
            csvs = os.listdir(DATA_DIR.joinpath(path).resolve())
            symbols = [csv.replace('.csv', '') for csv in csvs]
        for s in symbols:
            df = CSVDataloader.read_csv(s, path=path)
            if df is not None:
                dfs.append(df)

        df = pd.concat(dfs, axis=0)
        if set_index:
            df.set_index('date', inplace=True)
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True, ascending=True)
            df = df[start_date:]
            df = df[:end_date]
        else:
            df.sort_values(by='date', ascending=True, inplace=True)
            df = df[df['date'] >= start_date]
            df = df[df['date'] <= end_date]

        return df

    @staticmethod
    def calc_expr(df: pd.DataFrame, fields, names):
        cols = []
        count = 0
        df.set_index([df.index, 'symbol'], inplace=True)
        for field, name in tqdm(zip(fields, names)):
            try:
                if len(field) <= 0:
                    continue
                se = calc_expr(df, field)

                count += 1
                if count < 10:
                    df[name] = se
                else:
                    se.name = name
                    cols.append(se)
            except:
                print('{}错误'.format(field))
                import traceback
                print(traceback.print_exc())
                continue
        if len(cols):
            df_cols = pd.concat(cols, axis=1)
            df = pd.concat([df, df_cols], axis=1)

        # df_all = df.loc[self.start_date: self.end_date].copy()
        # print(df_all.index.levels[0])
        df['symbol'] = df.index.droplevel(0)
        # df_all['symbol'] = df_all.index.levels[0]
        df.index = df.index.droplevel(1)
        return df

    @staticmethod
    def get(symbols: list[str], col='close', start_date='20100101', end_date=datetime.now().strftime('%Y%m%d'),
            path='quotes'):
        df_all = CSVDataloader.get_df(symbols, set_index=True, path=path)
        if col not in df_all.columns:
            logger.error('{}列不存在')
            return None
        df_close = df_all.pivot_table(values=col, index=df_all.index, columns='symbol')
        df_close = df_close[start_date:]
        df_close = df_close[:end_date]
        return df_close

    @staticmethod
    def get_col_df(df_all, col='close', start_date='20100101', end_date=datetime.now().strftime('%Y%m%d'),
                   path='quotes'):
        if col not in df_all.columns:
            logger.error('{}列不存在')
            return None
        df_close = df_all.pivot_table(values=col, index=df_all.index, columns='symbol', dropna=False)
        df_close.ffill(inplace=True)
        df_close = df_close[start_date:]
        df_close = df_close[:end_date]
        if type(df_close) is pd.Series:
            df_close = df_close.to_frame()
        # df_close.fillna(0, inplace=True)
        df_close.dropna(inplace=True)
        return df_close

    @staticmethod
    def get_symbols_from_instruments(filename):
        with open(DATA_DIR.joinpath('instruments').joinpath(filename).resolve(), 'r') as f:
            symbols = f.readlines()

        symbols = [s.replace('\n', '') for s in symbols]
        return symbols


if __name__ == '__main__':
    import pandas as pd
    from datafeed.dataloader import CSVDataloader

    # symbols = CSVDataloader.get_symbols_from_instruments('1-商品期货流动性好的品类.txt')
    # symbols = ['B0','BR0']

    df = CSVDataloader.get_df(set_index=True, symbols=['510300.SH'])
    print(df)
    expr = 'RSRS(low,high,18)'
    df = CSVDataloader.calc_expr(df, ['roc(close,20)', 'kf(roc(close,18))'],
                                 ['roc_20', 'kf_roc'])
    print(df[['roc_20', 'kf_roc']])
