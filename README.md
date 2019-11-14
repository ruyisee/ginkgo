# ginkgo
股票行情数据本地化存储、并进行一些指标形态计算。 目前行情基于tushare

### 1.安装

#### 源码安装
```
git clone git@github.com:fsksf/ginkgo.git
cd ginkgo
pip install *
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

