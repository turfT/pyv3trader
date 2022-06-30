from typing import List
from pyv3trader.utils.types import StrategyStatus

def cal_usd_value(statu: StrategyStatus):
    token_num = statu.uncollected_othertoken+statu.othertoken_in_pool+statu.othertoken_in_wallet
    usd_num = statu.uncollected_usd+statu.usd_in_pool+statu.usd_in_wallet
    return token_num*float(statu.usd_price) + usd_num



def analyzer_summary(data:List[StrategyStatus]):
    days = (data[-1].timestamp - data[0].timestamp).days
    init_value = cal_usd_value(data[0])

    value_usd = [ cal_usd_value(status) for status in data]
    net_apr = (init_value/cal_usd_value(data[-1])-1)*365/days

    return {
        "days": days,
        "net_apr":net_apr,
    }