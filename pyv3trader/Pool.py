from typing import List
from pyv3trader.chainEventFeed import DataframeFeed
from pyv3trader.utils.helper import token_int_to_float, tick_to_usd_based_price, usd_based_price_to_tick
from pyv3trader.utils.types import PoolBaseInfo, ChainEvent,onchainTxType,Position
from pyv3trader.utils.liquitidymath import get_amounts,get_liquidity


class Pool():

    def __init__(self,pool_info:PoolBaseInfo):
        self.pool_basic_info = pool_info
        self.user_positions:List[Position] =[]# this list never pop.
        self.current_tick = None
        self.current_liquidity = None



    def get_positions(self):
        return self.user_positions

    @staticmethod
    def update_fee_for_one_position(event:ChainEvent,
                                    position:Position,
                                    current_liq:int,
                                    fee_rate:int)->Position:
        share = position.liquidity*1.0/current_liq
        is_token0_earned = event.amount0>0 # pool get amount 0 -> fee is amount 0
        if is_token0_earned:
            fee_earned =  int(event.amount0* fee_rate/1000000.0 * share)
            new_fee = fee_earned+position.uncollectedfee_token0

            return Position(
                lower_tick=position.lower_tick,
                upper_tick=position.upper_tick,
                liquidity=position.liquidity,
                uncollectedfee_token0=new_fee,
                uncollectedfee_token1=position.uncollectedfee_token1
            )

        else:
            fee_earned =  int(event.amount1* fee_rate/1000000.0 * share)
            new_fee = fee_earned + position.uncollectedfee_token1

            return Position(
                lower_tick=position.lower_tick,
                upper_tick=position.upper_tick,
                liquidity=position.liquidity,
                uncollectedfee_token0=position.uncollectedfee_token0 ,
                uncollectedfee_token1=new_fee
            )



    def update_fees(self, event:ChainEvent):
        for id,position in enumerate(self.user_positions):
            if position.upper_tick>event.current_tick and  position.lower_tick<event.current_tick:
                new_position = self.update_fee_for_one_position(event, position,event.current_liquidity,self.pool_basic_info.fee)
                self.user_positions[id] = new_position
            else:
                continue


    def handle_event(self, event:ChainEvent):
        self.current_tick = int(event.current_tick)
        self.current_liquidity  = event.current_liquidity
        if event.tx_type==onchainTxType.SWAP and len(self.user_positions)!=0:
            #update fee
            self.update_fees(event)



    def new_position(self,token0_amount:float,token1_amount:float,lower_tick,upper_tick,current_tick=None):
        if current_tick is None:
            current_tick =int( self.current_tick)
        token0_decimal,token1_decimal =self.pool_basic_info.token0_decimal, self.pool_basic_info.token1_decimal
        position_liq = get_liquidity(current_tick,lower_tick,upper_tick,token0_amount,
                                     token1_amount,token0_decimal,token1_decimal)
        token0_in_position, token1_in_position = get_amounts(current_tick,lower_tick,upper_tick,position_liq,
                                                             token0_decimal,token1_decimal)

        new_position = Position(
            lower_tick=lower_tick,
            upper_tick=upper_tick,
            liquidity=position_liq,
            uncollectedfee_token1=0,
            uncollectedfee_token0=0
        )

        self.user_positions.append(new_position)

        return token0_in_position,token1_in_position,new_position

    def close_position(self,_id):

        # collect fee
        collected_position = self.user_positions[_id]
        if collected_position.liquidity == 0:
            raise ValueError("closed already")
        token0_fee_float, token1_fee_float = self.get_uncollect_fee(collected_position)

        token0_from_pos, token1_from_pos  = self.get_token_amounts(collected_position)

        # reset
        self.user_positions[_id]._replace(liquidity=0,uncollectedfee_token0=0,uncollectedfee_token1=0)
        return token0_fee_float + token0_from_pos, token1_from_pos + token1_fee_float

    def add_liquidity(self):
        """
        add more liquidity for one position
        :return:
        """
        raise NotImplemented




    def get_uncollect_fee(self,uncollected_position:Position)->(float,float):
        uncollected_fee_0 = uncollected_position.uncollectedfee_token0
        uncollected_fee_1 = uncollected_position.uncollectedfee_token1

        fee_0_float = token_int_to_float(uncollected_fee_0,self.pool_basic_info.token0_decimal)
        fee_1_float = token_int_to_float(uncollected_fee_1,self.pool_basic_info.token1_decimal)
        return  fee_0_float,fee_1_float


    def get_token_amounts(self,pos:Position)->(float,float):
        return get_amounts(self.current_tick,
                            pos.lower_tick,
                            pos.upper_tick,
                            pos.liquidity,
                            self.pool_basic_info.token0_decimal,
                            self.pool_basic_info.token1_decimal)


    def swap(self,is_zero_for_one:bool,token_in_amount:float):
        current_price = self.get_usd_based_price()
        token0_is_usdlike = self.pool_basic_info.token0_is_usdlike
        pool_price = 1/ current_price if token0_is_usdlike else current_price

        if is_zero_for_one:
            return token_in_amount*pool_price#token out

        else:
            return token_in_amount/pool_price#token out

    def usd_to_num(self, usd, other_token_amount):
        return (usd, other_token_amount) if self.pool_basic_info.token0_is_usdlike \
            else (other_token_amount, usd)

    def num_to_usd(self, token0, token1):
        return (token0, token1) if self.pool_basic_info.token0_is_usdlike \
            else (token1, token0)

    def usd_based_price_to_tick(self,usd_price):
        return usd_based_price_to_tick(usd_price,self.pool_basic_info.token0_decimal,\
                                       self.pool_basic_info.token1_decimal,\
                                       self.pool_basic_info.token0_is_usdlike)

    def get_usd_based_price(self):
        return tick_to_usd_based_price(self.current_tick,
                                                self.pool_basic_info.token0_decimal,
                                                self.pool_basic_info.token1_decimal,
                                                self.pool_basic_info.token0_is_usdlike)

    def status(self):
        token0_total,token1_total,fee0_total,fee1_total = 0,0,0,0

        for pos in self.user_positions:
            fee0,fee1 = self.get_uncollect_fee(pos)
            token0,token1 = self.get_token_amounts(pos)
            token0_total+=token0
            token1_total+=token1
            fee0_total+=fee0
            fee1+=fee1


        return (token0_total,token1_total,fee0_total,fee1_total) if self.pool_basic_info.token0_is_usdlike else (token1_total,token0_total,fee1_total,fee0_total)




