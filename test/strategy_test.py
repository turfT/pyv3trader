import os
import config
from datetime import datetime,timedelta

from pyv3trader.utils.types import PoolBaseInfo
from pyv3trader.analyzer import analyzer_summary

import os
from decimal import Decimal

import config
from datetime import datetime, timedelta



from pyv3trader.chainEventFeed import DataframeFeed
from pyv3trader.preprocess import preprocess
import unittest
from pyv3trader.utils.types import ChainEvent, PoolBaseInfo, Position
from pyv3trader.Pool import Pool
from pyv3trader.Strategy import Strategy
from pyv3trader.utils.helper import tick_to_usd_based_price, usd_based_price_to_tick

pool_info = PoolBaseInfo(
    token0="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    token1="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
    pool="0xdc0e7aCE1efEfbd7cdaF0768C8079e7d6007d727",
    fee=500,
    tickSpacing=10,
    token0_decimal=6,
    token1_decimal=18,
    token0_is_usdlike=True

)

end = datetime(2022, 5, 20)
start = end - timedelta(days=20)
my_path = os.getcwd() + '//data'
pool_address = "0x45dda9cb7c25131df268515131f647d726f50608"
merge_data = preprocess(pool_address, start, end, my_path)

class DemoStrategy(Strategy):
    def on_start(self):
        super(DemoStrategy,self).on_start()

        current_price = tick_to_usd_based_price(self.pool.current_tick,
                                                pool_info.token0_decimal,
                                                pool_info.token1_decimal,
                                                pool_info.token0_is_usdlike)

        upper_price = current_price * Decimal("1.1")
        lower_price = current_price / Decimal("1.1")

        init_value = self.usd_amount+current_price*self.other_token_amount
        print("init_value",init_value)

        self.new_position(
            self.usd_amount,
            self.other_token_amount,
            upper_price,
            lower_price
        )



class TestStrategy(unittest.TestCase):
    def setUp(self):
        self.my_mock_pool = Pool(pool_info)
        data_feed = DataframeFeed(merge_data)
        self.strategy = DemoStrategy(data_feed,pool_info,20000,1)



    def test_analyzer(self):
        strategy_res = self.strategy.run()

        summary =analyzer_summary(strategy_res)
        print(summary)










