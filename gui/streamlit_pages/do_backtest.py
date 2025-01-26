import re
from pydantic import Field
from typing import List

import sys
from pathlib import Path
from datetime import datetime

# sys.path.append(str(Path(__file__).resolve().parent.parent.parent / 'lab'))
# print(sys.path)

from bt_algos_extend import Task, Engine
from config import get_all_factors

all_factors = get_all_factors()

from pydantic import BaseModel, Extra



class Ind(BaseModel):
    ind: str = '动量(20)'
    op: str = '>'
    value: float = 0.0

    def transform(self, s):
        if '(' not in s:
            return s
        # 使用正则表达式匹配函数名和参数
        match = re.match(r"([A-Za-z\u4e00-\u9fa5]+)\((.*)\)", s)
        if match:
            # 提取函数名
            func_name = match.group(1)
            # 提取匹配的参数字符串
            params_str = match.group(2)

            # 组合新的字符串
            transformed_str = f"{func_name}_{params_str.replace(',', '_')}"
            return transformed_str
        else:
            return "没有匹配到结果"

    def get_ind_expr(self):
        # name = self.ind = 动量(20)
        # field = roc(close,20)
        return f'{self.transform(self.ind)}{self.op}{self.value}'

    def parse_ind_name(self):
        if '(' not in self.ind:
            return self.ind
        match = re.match(r"([A-Za-z\u4e00-\u9fa5]+)\((.*)\)", self.ind)
        if match:
            # 提取函数名
            func_name = match.group(1)
            # 提取匹配的参数字符串
            params_str = match.group(2)
            # 提取所有参数并转换为整数列表，假设参数都是整数
            # 如果参数可能不是整数，需要对每个参数进行适当的解析
            numbers = [param for param in re.split(r',\s*', params_str) if param]
            # 输出结果
            print(f"函数名:{func_name},以及数值列表:{numbers}")

            if func_name in all_factors.keys():
                expr = all_factors[func_name]['expr']
                for i, n in enumerate(numbers):
                    expr = expr.replace(f'$P{i + 1}', n)
                # expr = expr.replace('PARAMS', ','.join(numbers))
                return expr
        else:
            print("没有匹配到结果")
            return None


class Orderby(BaseModel):
    ind: str
    direction: int
    weight: float

    def transform(self, s):
        if '(' not in s:
            return s
        # 使用正则表达式匹配函数名和参数
        match = re.match(r"([A-Za-z\u4e00-\u9fa5]+)\((.*)\)", s)
        if match:
            # 提取函数名
            func_name = match.group(1)
            # 提取匹配的参数字符串
            params_str = match.group(2)

            # 组合新的字符串
            transformed_str = f"{func_name}_{params_str.replace(',', '_')}"
            return transformed_str
        else:
            return "没有匹配到结果"

    def parse_ind_name(self):
        if '(' not in self.ind:
            return self.ind
        match = re.match(r"([A-Za-z\u4e00-\u9fa5]+)\((.*)\)", self.ind)
        if match:
            # 提取函数名
            func_name = match.group(1)
            # 提取匹配的参数字符串
            params_str = match.group(2)
            # 提取所有参数并转换为整数列表，假设参数都是整数
            # 如果参数可能不是整数，需要对每个参数进行适当的解析
            numbers = [param for param in re.split(r',\s*', params_str) if param]
            # 输出结果
            print(f"函数名:{func_name},以及数值列表:{numbers}")

            if func_name in all_factors.keys():
                expr = all_factors[func_name]['expr']
                for i, n in enumerate(numbers):
                    expr = expr.replace(f'$P{i + 1}', n)
                # expr = expr.replace('PARAMS', ','.join(numbers))
                return expr
        else:
            print("没有匹配到结果")
            return None


class TaskInfo(Task, BaseModel, extra=Extra.ignore):
    buy_rules: List[Ind] = Field(default_factory=list)
    sell_rules: List[Ind] = Field(default_factory=list)
    orderby_rules: List[Orderby] = Field(default_factory=list)
    access_type: str = 'public'
    points: int = 1


def backtest(task_info: TaskInfo, no_orders=False):
    # 把buy_rules和sell_rules转为select_buy和select_sell的信号规则
    task_info.names = []
    task_info.fields = []
    if len(task_info.buy_rules):
        task_info.select_buy = []
        for r in task_info.buy_rules:
            task_info.select_buy.append(r.get_ind_expr())
            if r.transform(r.ind) not in task_info.names:
                task_info.names.append(r.transform(r.ind))
                task_info.fields.append(r.parse_ind_name())

    if len(task_info.sell_rules):
        task_info.select_sell = []
        for r in task_info.sell_rules:
            task_info.select_sell.append(r.get_ind_expr())
            if r.transform(r.ind) not in task_info.names:
                task_info.names.append(r.transform(r.ind))
                task_info.fields.append(r.parse_ind_name())

    if len(task_info.orderby_rules):
        if len(task_info.orderby_rules) == 1:
            r = task_info.orderby_rules[0]
            expr = r.transform(r.ind)
            if r.transform(r.ind) not in task_info.names:
                task_info.names.append(r.transform(r.ind))
                task_info.fields.append(r.parse_ind_name())
        else:
            expr = None
            for r in task_info.orderby_rules:
                if r.transform(r.ind) not in task_info.names:
                    task_info.names.append(r.transform(r.ind))
                    task_info.fields.append(r.parse_ind_name())

                if not expr:
                    expr = f'rank({r.transform(r.ind)})*r.weight*r.direction'
                else:
                    expr = expr + "+" + f'rank({r.transform(r.ind)})*r.weight*r.direction'

        task_info.order_by_signal = expr

    res = Engine().run(task_info)
    # print(res.stats)
    # print(res.prices)
    ratios = []
    for s in ['策略', 'benchmark']:
        ratio = {}
        for item in ['cagr', 'total_return', 'max_drawdown', 'calmar', 'daily_sharpe']:
            ratio.update({item: round(res.stats.loc[item][s], 2)})
        ratios.append(ratio)
    print(res.prices)
    quotes = (res.prices.pct_change() + 1).cumprod().dropna()
    quotes['date'] = quotes.index
    quotes['date'] = quotes['date'].apply(lambda x: x.strftime('%Y%m%d'))

    rets = {
        'ratio': ratios,
        'res': res,
        'quotes': quotes.to_dict(orient='records'),

    }
    if not no_orders:
        rets['df_quotes'] = quotes
        rets['orders'] = res.get_transactions()

    # print(rets)
    return rets
