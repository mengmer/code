# 克隆自聚宽文章：https://www.joinquant.com/post/34011
# 标题：二板排板战法研究
# 作者：游资小码哥

# 导入函数库
from jqdatasdk import *
from datetime import datetime, timedelta
import logging as log
import pandas as pd
from typing import Dict, Optional, List, Any

## 模拟聚宽context
class portfolio:
    def __init__(self):
        self.available_cash = 10000

class context():
    def __init__(self):

        self.portfolio = portfolio()
        # 运行参数
        self.run_params = 1

        # 股票池 list
        self.universe = 1

        # 时间
        self.current_dt = datetime.today()

        # 前一个交易日
        yesterday = (self.current_dt + timedelta(days=-1)).strftime("%Y-%m-%d")  # '2021-01-15'#datetime.datetime.now()
        yesterday_a_month_ago = (self.current_dt + timedelta(days=-30)).strftime("%Y-%m-%d")
        trade_date = get_trade_days(start_date=yesterday_a_month_ago, end_date=yesterday, count=None)
        self.previous_date = trade_date[-1]

        # 子账户信息
        self.subportofolio = 1


    pass

## 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')
    # g 内置全局变量
    g.my_security = '510300.XSHG'
    set_universe([g.my_security])

    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5),
                   type='stock')

    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
    # 开盘前运行
    run_daily(before_market_open, time='before_open', reference_security='000300.XSHG')
    # 开盘时运行
    run_daily(market_run, time='every_bar', reference_security='000300.XSHG')
    # run_daily(market_run_sell, time='every_bar', reference_security='000300.XSHG')

    # 收盘后运行before_open
    # run_daily(before_market_open, time='after_close', reference_security='000300.XSHG')

buy_bool = False

## 开盘前运行函数 选择二板放量股  并且横盘震荡
def before_market_open(context):
    '''
    :param context: 输入context对象
    :return: 开盘前运行函数
    '''
    trade_stock_list = []

    # 1、选取股票池, 并剔除ST、退市、科创板股票
    codes_list = stocks_filter()
    df_stocks_last_2_days = get_price(codes_list, count=2, end_date=context.previous_date, frequency='daily',
                         fields=['open', 'close', 'high_limit', 'money', 'pre_close'], panel=False)
    # 2、选取连板股票
    # 1板涨停，并且涨停价大于105%昨日收盘价，收盘价>105%开盘价（剔除一字板的情况）
    stock_list = df_stocks_last_2_days[(df_stocks_last_2_days.close == df_stocks_last_2_days.high_limit)
                                 & (df_stocks_last_2_days.high_limit >= df_stocks_last_2_days.pre_close * 1.05)
                                 & (df_stocks_last_2_days.close >= df_stocks_last_2_days.open * 1.05)]
    # 2连板股票
    stock_list = stock_list[stock_list.duplicated('code')]
    stock_list = stock_list['code'].tolist()

    # 3、查看股票前期是否平整，并且股票第一个板要高过60个交易日的最高收盘价
    flat_factor = {"flat_factor_10": {'days': 10, '1.5%': 3, '3%': 5, '5.5%': 7},
                   "flat_factor_20": {'days': 20, '1.5%': 7, '3%': 15, '5.5%': 18},
                   "flat_factor_30": {'days': 30, '1.5%': 13, '3%': 16, '5.5%': 26},
                   "flat_factor_60": {'days': 60, '1.5%': 28, '3%': 45, '5.5%': 50},
                   }
    for stock in stock_list:
        if filter_flat_stock_1(stock, end_date=context.previous_date, flat_factor=flat_factor['flat_factor_20']):
            if filter_flat_stock_1(stock, end_date=context.previous_date, flat_factor=flat_factor['flat_factor_60']):
                trade_stock_list.append(stock)
        else:
            print(stock, '未通过检验')

    return trade_stock_list

## 开盘时运行函数
def market_run(context, trade_stock_list):
    time_now = context.current_dt.strftime('%H:%M:%S')
    time_1030 = datetime.strptime('10:30:00', '%H:%M:%S').strftime('%H:%M:%S')
    now = context.current_dt
    time_today_zero = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                         microseconds=now.microsecond)

    time_today_931 = time_today_zero + timedelta(hours=9, minutes=31, seconds=00)
    # trade_stock_list = ['000665.XSHE']
    # 买入
    if len(trade_stock_list) > 0:
        for stock in trade_stock_list:
            # log.info("当前时间 %s" % (context.current_dt))
            # log.info("股票 %s 的最新价: %f" % (stock, get_current_data()[stock].last_price))
            cash = context.portfolio.available_cash
            # print(cash)
            current_price = get_current_data()[stock].last_price
            day_open_price = get_current_data()[stock].day_open
            day_high_limit = get_current_data()[stock].high_limit
            pre_date = (context.current_dt + timedelta(days=-1)).strftime("%Y-%m-%d")
            df_panel = get_price(stock, count=1, end_date=pre_date, frequency='daily',
                                 fields=['open', 'high', 'close', 'low', 'high_limit', 'money', 'pre_close'], panel=False)
            pre_high = df_panel['high'].values
            pre_close = df_panel['close'].values
            df_panel_all = get_price(stock, start_date=time_today_931, end_date=context.current_dt, frequency='minute',
                                     fields=['high', 'low', 'close', 'high_limit', 'money'], panel=False)
            min_close_price = df_panel_all.loc[:, "close"].min()
            max_close_price = df_panel_all.loc[:, "close"].max()
            # 分钟行情中有几次打到板
            count_max = (df_panel_all.loc[:, 'close'] == df_panel_all.loc[:, 'high_limit']).sum()

            if cash > 5000 and count_max > 3:
                # 当前价格>昨日收盘价1.07 & 当前价格<股票涨停价 & 开盘价小于涨停价的98% 防止打不进去
                if current_price > pre_close * 1.07 and current_price < day_high_limit and day_open_price < day_high_limit * 0.98:
                    # open_cash = cash / len(trade_stock_list)
                    print(stock + "1.买入金额" + str(cash))
                    # 用现金全部买入
                    order_value(stock, cash)
                    trade_stock_list.remove(stock)

    time_sell = context.current_dt.strftime('%H:%M:%S')
    time_1440 = datetime.strptime('14:40:00', '%H:%M:%S').strftime('%H:%M:%S')

    # 下午14：40分之后卖出
    if time_sell > time_1440:
        portfolio_stock_list = context.portfolio.positions
        if len(portfolio_stock_list) > 0:
            for sell_stock in portfolio_stock_list:
                current_price_list = get_ticks(sell_stock, start_dt=None, end_dt=context.current_dt, count=1,
                                               fields=['time', 'current', 'high', 'low', 'volume', 'money'])
                current_price = current_price_list['current'][0]
                day_open_price = get_current_data()[sell_stock].day_open
                day_high_limit = get_current_data()[sell_stock].high_limit
                day_low_limit = get_current_data()[sell_stock].low_limit

                # 查询当天的最高价
                df_panel_allday = get_price(sell_stock, start_date=time_today_931, end_date=context.current_dt,
                                            frequency='minute', fields=['high', 'low', 'close', 'high_limit', 'money'], panel=False)
                min_low_price = df_panel_allday.loc[:, "low"].min()
                max_high_price = df_panel_allday.loc[:, "high"].max()
                ##获取前一天的收盘价
                pre_date = (context.current_dt + timedelta(days=-1)).strftime("%Y-%m-%d")
                df_panel = get_price(sell_stock, count=1, end_date=pre_date, frequency='daily',
                                     fields=['open', 'close', 'high_limit', 'money', 'low', ], panel=False)
                pre_low_price = df_panel['low'].values
                pre_close_price = df_panel['close'].values
                # 30日行情中有几次打到板
                num_limit_stock = count_limit_num_all(sell_stock, context)
                # 平均持仓成本
                cost = context.portfolio.positions[sell_stock].avg_cost
                # print("----------------------------------")
                # print("current_price="+str(current_price))
                # print("day_open_price="+str(day_open_price))
                # print("pre_close_price="+str(pre_close_price))
                # print("df_max_high="+str(df_max_high))
                # print("=====================================")
                # 如果当前价格<最高价的0.97 & 当前价格>一日最低价
                if current_price < max_high_price * 0.97 and current_price > day_low_limit:
                    print("1.卖出股票：小于最高价0.97倍" + str(num_limit_stock))
                    order_target(sell_stock, 0)
                elif current_price < cost * 0.93 and current_price < day_open_price and current_price > day_low_limit:
                    print("卖出股票：比开盘价低7个点" + str(num_limit_stock))
                    order_target(sell_stock, 0)

    # 上午10：30分之后卖出
    elif time_sell > time_1030:
        stock_owner = context.portfolio.positions
        if len(stock_owner) > 0:
            for stock_two in stock_owner:
                current_price_list = get_ticks(stock_two, start_dt=None, end_dt=context.current_dt, count=1,
                                               fields=['time', 'current', 'high', 'low', 'volume', 'money'])
                current_price = current_price_list['current'][0]
                day_open_price = get_current_data()[stock_two].day_open
                day_high_limit = get_current_data()[stock_two].high_limit
                day_low_limit = get_current_data()[stock_two].low_limit

                # 查询当天的最高价
                df_panel_allday = get_price(stock_two, start_date=lastToday, end_date=context.current_dt,
                                            frequency='minute', fields=['high', 'low', 'close', 'high_limit', 'money'], panel=False)
                min_low_price = df_panel_allday.loc[:, "low"].min()
                max_high_price = df_panel_allday.loc[:, "high"].max()
                ##获取前一天的收盘价
                pre_date = (context.current_dt + timedelta(days=-1)).strftime("%Y-%m-%d")
                df_panel = get_price(stock_two, count=1, end_date=pre_date, frequency='daily',
                                     fields=['open', 'close', 'high_limit', 'money', 'low', ], panel=False)
                pre_low_price = df_panel['low'].values
                pre_close_price = df_panel['close'].values
                num_limit_stock = count_limit_num_all(stock_two, context)
                # 平均持仓成本
                cost = context.portfolio.positions[stock_two].avg_cost
                # print("----------------------------------")
                # print("current_price="+str(current_price))
                # print("day_open_price="+str(day_open_price))
                # print("pre_close_price="+str(pre_close_price))
                # print("df_max_high="+str(df_max_high))
                # print("=====================================")
                if current_price < pre_close_price * 1.03 and current_price > day_low_limit:
                    print("1.卖出股票：小于最高价0.97倍" + str(num_limit_stock))
                    order_target(stock_two, 0)

    time_sell = context.current_dt.strftime('%H:%M:%S')
    time_1440 = datetime.datetime.strptime('14:45:00', '%H:%M:%S').strftime('%H:%M:%S')
    if time_sell > time_1440 and len(trade_stock_list) > 0:
        instead_stock = trade_stock_list
        for stock_remove in instead_stock:
            trade_stock_list.remove(stock_remove)

## 收盘后运行函数
def after_market_close(context):
    log.info(str('除当天的股票数据-----函数运行时间(after_market_close):' + str(context.current_dt.time())))

    # 给老婆的检讨书
    # FIRST OF ALL I am so SORRY for breaking your heart babe
    # 对此为自己做错的事情向老婆做出深刻检讨
    # 1. what
    # 我们的感情一直很好，你给我的爱是前所未有的体验，可是我的行为给我们的感情带来了不好的影响，我真的很内疚很羞愧
    # 真的很抱歉让你失望了，我没有我以为的那么好，可是我现在很后怕因为我不想失去你，不能没有你
    # 这两天一直在想，想很多，虽然你一直告诉我不会离开我，可是想到你对我的爱会减少心脏就会很痛
    #
    # 消除当天的股票数据
    trade_stock_list = []
    # print(trade_stock_list)

## 辅助函数 筛选股票
def stocks_filter(df_stocks = None):
    '''
    :param df_stocks: 传入股票数据
    :return: 筛选后的股票 剔除ST、退市、创业板、科创板、上市时间等元素
    '''
    if isinstance(df_stocks, pd.DataFrame):
        df_all_stocks = df_stocks
    else:
        df_all_stocks = get_all_securities(['stock'])
    df_all_stocks['code'] = df_all_stocks.index.values
    df_all_stocks.reset_index(inplace=True, drop=True)
    # 剔除ST、退市、科创板
    df_all_stocks = df_all_stocks[(df_all_stocks.display_name.str.contains('ST') == False) & (
                df_all_stocks.display_name.str.contains('退') == False) &
                                  (df_all_stocks.code.str.startswith('300') == False) & (
                                              df_all_stocks.code.str.startswith('688') == False)]

    stock_code_list = df_all_stocks['code'].tolist()
    # 剔除上市时间
    # for stock in stock_code_list:
    #     # days_public=(context.current_dt.date() - get_security_info(stock).start_date).days days_public > days and
    #     market_cap = get_circulating_market_cap(stock)
    #     market_cap_num = market_cap['circulating_market_cap'].values
    #     if market_cap_num < 10 and market_cap_num > 150:
    #         stock_code_list.remove(stock)

    return stock_code_list

def filter_flat_stock_1(stock, end_date, flat_factor: dict):
    # 查询昨天的涨停价格
    df_flat_sotck = get_price(stock, end_date=end_date, count=flat_factor['days'],  frequency='daily',
                         fields=['open', 'close', 'high_limit', 'money', 'high', 'low'], panel=False)
    # 因子计算
    abs_sum_factor = (df_flat_sotck.loc[:, 'close'] - df_flat_sotck.loc[:, 'open']).abs() / (
            (df_flat_sotck.loc[:, 'open'] + df_flat_sotck.loc[:, 'close']) / 2)
    # 因子波动率小于 1.5%, 3%, 5% 的个数
    factor_15 = (abs_sum_factor < 0.015).sum()  # 波动率1.5%
    factor_30 = (abs_sum_factor < 0.03).sum() # 波动率3%
    factor_55 = (abs_sum_factor < 0.055).sum() # 波动率5.5%
    if factor_15 >= flat_factor['1.5%'] and factor_30 >= flat_factor['3%'] and factor_55 >= flat_factor['5.5%']:
        if flat_factor['days'] == 60:
            if df_flat_sotck.loc[df_flat_sotck.index.max(), 'close'] * 1.1 > df_flat_sotck["open"].max():
                return True
        else:
            return True

##查看他总的涨停数
def count_limit_num_all(stock, context):
    date_now = (context.current_dt + timedelta(days=-1)).strftime("%Y-%m-%d")  # '2021-01-15'#datetime.datetime.now()
    yesterday = (context.current_dt + timedelta(days=-30)).strftime("%Y-%m-%d")
    trade_date = get_trade_days(start_date=yesterday, end_date=date_now, count=None)
    limit_num = 0
    for datenum in trade_date:
        df_panel = get_price(stock, count=1, end_date=datenum, frequency='daily',
                             fields=['open', 'close', 'high_limit', 'money'], panel=False)
        df_close = df_panel['close'].values
        df_high_limit = df_panel['high_limit'].values
        if df_close == df_high_limit:
            limit_num = limit_num + 1
    return limit_num

##获取个股流通市值数据
def get_circulating_market_cap(stock_list):
    query_list = [stock_list]
    q = query(valuation.code, valuation.circulating_market_cap).filter(valuation.code.in_(query_list))
    market_cap = get_fundamentals(q)
    market_cap.set_index('code', inplace=True)
    return market_cap


if __name__ == "__main__":


    auth('13602601626', 'Xm19970711')
    context = context()
    trade_stock_list = before_market_open(context=context)
    market_run(context, trade_stock_list)
