import pandas as pd

from pyv3trader.utils.types import ChainEvent,onchainTxType
from dateutil import parser


class DataframeFeed():
    def __init__(self,df:pd.DataFrame):
        self.df = df
        self.row_iter = self.df.iterrows()

    def __iter__(self):
        return self.row_iter

        # yield ChainEventData(
        #     block_number=an_event.block_number,
        #     block_timestamp=parser.parse(an_event.block_timestamp),
        #     transaction_index=an_event.transaction_index,
        #     log_index=an_event.log_index,
        #     tx_type=txType[str(an_event.tx_type)],
        #     amount0=an_event.amount0,
        #     amount1=an_event.amount1,
        #     current_liquidity=an_event.current_liquidity,
        #     current_tick=an_event.current_tick
        # )

    def setFromDataFrame(self,df:pd.DataFrame):
        self.__init__(df)

    def getNextChainEvent(self):
        _,an_event = next(self.__iter__())
        return ChainEvent(
            block_number=an_event.block_number,
            block_timestamp=parser.parse(an_event.block_timestamp),
            transaction_index=an_event.transaction_index,
            log_index=an_event.log_index,
            tx_type=onchainTxType[str(an_event.tx_type)],
            amount0=an_event.amount0,
            amount1=an_event.amount1,
            current_liquidity=int(an_event.current_liquidity),
            current_tick=int(an_event.current_tick)
        )



