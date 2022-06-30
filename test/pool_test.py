import os
from decimal import Decimal

import config
from datetime import datetime, timedelta


pool_address = "0x45dda9cb7c25131df268515131f647d726f50608"
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
    pool="0x45dda9cb7c25131df268515131f647d726f50608",
    fee=500,
    tickSpacing=10,
    token0_decimal=6,
    token1_decimal=18,
    token0_is_usdlike=True

)

mock_position1 = Position(
    lower_tick=199872 - 200,
    upper_tick=201360 + 100,
    liquidity=992928474714321,
    uncollectedfee_token0=0,
    uncollectedfee_token1=0
)

mock_position2 = Position(
    lower_tick=200,
    upper_tick=20000,
    liquidity=1000000000000,
    uncollectedfee_token0=0,
    uncollectedfee_token1=0
)
end = datetime(2022, 5, 20)
start = end - timedelta(days=2)
my_path = os.getcwd() + '//data'

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

    def test_update_fee(self):

        self.my_mock_pool.user_positions.append(mock_position1)
        self.my_mock_pool.user_positions.append(mock_position2)
        one_event = self.strategy.feed.getNextChainEvent()

        self.assertEqual(200762,one_event.current_tick)
        self.my_mock_pool.update_fees(one_event)
        print(one_event)
        for pos in self.my_mock_pool.user_positions:
            print(pos)

    def test_on_event(self):
        self.my_mock_pool.user_positions.append(mock_position1)
        self.strategy.run()
        for pos in self.my_mock_pool.user_positions:
            print(pos)

    def test_new_position(self):
        first_event =self.strategy.feed.getNextChainEvent()
        current_tick = first_event.current_tick
        current_liq = first_event.current_liquidity
        self.strategy.pool.current_tick = current_tick
        self.strategy.pool.current_liquidity = current_liq



        self.strategy.run()

        print(self.strategy.usd_amount,self.strategy.other_token_amount)
        current_price =tick_to_usd_based_price( int(self.strategy.pool.current_tick),
                                                self.strategy.pool.pool_basic_info.token0_decimal,
                                                self.strategy.pool.pool_basic_info.token1_decimal,
                                                self.strategy.pool.pool_basic_info.token0_is_usdlike)
        print("final_value",self.strategy.usd_amount+self.strategy.other_token_amount*float(current_price ))