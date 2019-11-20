# ginkgo
股票行情数据本地化存储、并进行一些指标形态计算。 目前行情基于tushare

### 1.安装

#### 源码安装
```
git clone git@github.com:fsksf/ginkgo.git
cd ginkgo
pip install .
```

### 命令介绍
```
Usage: ginkgo  COMMAND [OPTIONS] [ARGS]...

Options:
  -h, --help  请选择要执行的command

Commands:
  calc-classical    # 经典形态选股
  gen-config        # 获取默认配置到用户家目录
  quote-init        # 行情数据初始化
  quote-update      # 行情数据更新
```

### 使用本地数据源
```
from ginkgo.data_local.data_proxy import DataProxy
dp = DataProxy()
# 获取一段时间的交易日历
dp.get_calendar(start_date, end_date)
# 获取symbol， 支持过滤
dp.get_symbols(industry=None, area=None, board=None, symbol=True)
# 从start_date 偏移几个交易日历天， 整数向前偏移 ，负数向后偏移
dp.get_date_offset(start_date, bar_cunt)
# 获取一个symbol的历史数据， 返回自定义Frame类型, 可以使用to_dataframe 转为pandas.DataFrame
dp.get_daily_hist(symbol, start_date, end_date, fields_list=None, br=False)
# 获取多个symbol的历史数据， 返回自定义SFrame类型, 可以使用to_dataframe 转为pandas.DataFrame
dp.get_daily_hists(symbols, start_date, end_date, fields_list=None, br=False)
```