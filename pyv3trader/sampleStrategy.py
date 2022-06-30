from Strategy import Strategy
from pyv3trader.chainEventFeed import DataframeFeed
from pyv3trader.utils.types import PoolBaseInfo


class buy_hold_Strategy(Strategy):

    def __init__(self,feed:DataframeFeed,pool_info:PoolBaseInfo,eth = 1, usdc = 2000):
        super(Strategy,self).__init__(feed,pool_info,other_token_amount=eth,usd_amount= usdc)





