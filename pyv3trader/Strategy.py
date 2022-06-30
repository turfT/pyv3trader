import datetime
from typing import List

from pyv3trader.Pool import Pool
from pyv3trader.chainEventFeed import DataframeFeed
from pyv3trader.utils.types import PoolBaseInfo, ChainEvent, StrategyStatus
from pyv3trader.utils.helper import usd_based_price_to_tick
from dateutil import parser
from pyv3trader.utils.types import ChainEvent, onchainTxType
import pandas as pd


class Strategy():
    def __init__(self, feed: DataframeFeed, pool_info: PoolBaseInfo, usd_amount:float, other_token_amount:float):
        self.pool = Pool(pool_info)
        self.feed = feed
        self.usd_amount = usd_amount
        self.other_token_amount = other_token_amount
        self.token0_decimal = pool_info.token0_decimal
        self.token1_decimal = pool_info.token0_decimal
        self.token0_is_usdlike = pool_info.token0_is_usdlike

        self.status_series:List[StrategyStatus]=[]

    def get_position(self):
        return self.pool.user_positions

    def new_position(self, usd, other_token_amount, usd_price_a, usd_price_b):
        if (usd > self.usd_amount or other_token_amount > self.other_token_amount):
            raise ValueError("insufficient funds")
        token0_amount, token1_amount = self.pool.usd_to_num(usd, other_token_amount)
        tick_a = self.pool.usd_based_price_to_tick(usd_price_a)
        tick_b = self.pool.usd_based_price_to_tick(usd_price_b)
        token0_used, token1_used, new_position = self.pool.new_position(token0_amount, token1_amount, tick_a, tick_b)
        usd_used, other_token_used = self.pool.num_to_usd(token0_used, token1_used)
        # change balance
        self.usd_amount -= usd_used
        self.other_token_amount -= other_token_used
        return new_position

    def close_position(self, _id):
        token0_get, token1_get = self.pool.close_position(_id)
        usd_get, other_token_get = self.pool.num_to_usd(token0_get, token1_get)
        self.usd_amount += usd_get
        self.other_token_amount += other_token_get

    def get_status(self, timestamp: datetime.datetime) -> StrategyStatus:

        usd_in_pool,other_token_in_pool,usd_fee,other_token_fee = self.pool.status()
        return StrategyStatus(
            timestamp,
            self.usd_amount,
            self.other_token_amount,
            self.pool.get_usd_based_price(),
            usd_in_pool,
            other_token_in_pool,
            usd_fee,
            other_token_fee
        )

    def on_event(self, an_event: ChainEvent):
        self.pool.handle_event(an_event)
        self.status_series.append(self.get_status(an_event.block_timestamp))

    def on_start(self):
        an_event = self.feed.getNextChainEvent()
        self.pool.handle_event(an_event)
        self.status_series.append(self.get_status(an_event.block_timestamp))

    def on_end(self):
        print("on end position", self.pool.user_positions)
        timestamp = self.status_series[-1].timestamp
        for _id, _ in enumerate(self.pool.user_positions):
            self.close_position(_id)
        self.status_series.append(self.get_status(timestamp))

    def run(self):
        self.on_start()
        for _, an_event in self.feed:
            chain_event = ChainEvent(
                block_number=an_event.block_number,
                block_timestamp=parser.parse(an_event.block_timestamp),
                transaction_index=an_event.transaction_index,
                log_index=an_event.log_index,
                tx_type=onchainTxType[str(an_event.tx_type)],
                amount0=an_event.amount0,
                amount1=an_event.amount1,
                current_liquidity=an_event.current_liquidity,
                current_tick=an_event.current_tick
            )
            self.on_event(chain_event)

        self.on_end()
        return self.status_series
