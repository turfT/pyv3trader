# Uniswap v3 backtest framework

## introduction
this repository is my backtester for uniswap v3 maker strategy.

inspired by [gammaStrategy](https://github.com/GammaStrategies/active-strategy-framework) and pyalgotrade.
with following features:

1. based on chain event
2. add some abstract about pool and strategy

## data download
same as [gammaStrategy](https://github.com/GammaStrategies/active-strategy-framework) repository. 
Use Google BigQuery.  

```
**blockhain-etl via Google BigQuery **

The pattern to use these data sources can be seen in [3_Uniswap_Simulation.ipynb](3_Uniswap_Simulation.ipynb). The data sources is [blockchain-etl](https://github.com/blockchain-etl), which indexes the relevant events from Uniswap v3, and can be easily queried through Google's BigQuery service. This data source can offer all the required fields for the simulations, but may incur a cost.  

*Instructions*
1. Install [Python client for Google BigQuery](https://github.com/googleapis/python-bigquery)
2. Generate a [service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) and download to your computer
3. Generate a file called ```config.py``` in the directory where the ActiveStrategyFramework is stored and point the direction of the file as a variable called ```GOOGLE_SERVICE_AUTH_JSON```  (eg. ```GOOGLE_SERVICE_AUTH_JSON=/point/to/file/auth_key.json```)
```

run [big_query_downloader.py](pyv3trader/big_query_downloader.py) to download data.


## how to backtest

run test.

