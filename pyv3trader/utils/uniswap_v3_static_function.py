from decimal import Decimal, getcontext, ROUND_UP, ROUND_DOWN
from typing import Optional


def get_amount0_delta(sqrt_price_a: Decimal, sqrt_price_b: Decimal, liquidity, round_up: Optional[bool]):
    '''
    Gets the amount0 delta between two prices
    :param sqrt_price_a:
    :param sqrt_price_b:
    :param liquidity:
    :param round_up:
    :return:amount0 Amount of token0 required to cover a position of size liquidity between the two passed prices
    '''
    if round_up is None:
        if liquidity < 0:
            return - get_amount0_delta(sqrt_price_a, sqrt_price_b, -liquidity, False)
        else:
            return get_amount0_delta(sqrt_price_a, sqrt_price_b, liquidity, True)

    if sqrt_price_a > sqrt_price_b:
        sqrt_price_a, sqrt_price_b = sqrt_price_b, sqrt_price_a


    diff = sqrt_price_b - sqrt_price_a

    if round_up:
        print("liquidity:",liquidity)
        print("diff",diff)
        return ((liquidity * diff / sqrt_price_b).quantize(Decimal('1'), rounding=ROUND_UP) / sqrt_price_a).quantize(
            Decimal('1'), rounding=ROUND_UP)
    else:
        return ((liquidity * diff / sqrt_price_b).quantize(Decimal('1'), rounding=ROUND_DOWN) / sqrt_price_a).quantize(
            Decimal('1'), rounding=ROUND_DOWN)


def get_amount1_delta(sqrt_price_a: Decimal, sqrt_price_b: Decimal, liquidity, round_up: Optional[bool]):
    if round_up is None:
        if liquidity < 0:
            return -get_amount1_delta(sqrt_price_a, sqrt_price_b, -liquidity, False)
        else:
            return get_amount1_delta(sqrt_price_a, sqrt_price_b, liquidity, True)
    if sqrt_price_a > sqrt_price_b:
        sqrt_price_a, sqrt_price_b = sqrt_price_b, sqrt_price_a
    diff = sqrt_price_b - sqrt_price_a
    print("diff of get_amount1_delta ", diff)
    if round_up:
        return (liquidity * diff).quantize(Decimal("1"), rounding=ROUND_UP)
    else:
        return (liquidity * diff).quantize(Decimal("1"), rounding=ROUND_DOWN)


def get_next_sqrt_price_from_amount0_rounding_up(sqrt_price:Decimal, liquidity:Decimal, amount_in:Decimal, add):
    """
    :param sqrt_price:
    :param liquidity:
    :param amount_in:How much of token0 to add or remove from virtual reserves
    :param add:Whether to add or remove the amount of token0
    :return: The price after adding or removing amount, depending on add
    """
    if amount_in == 0: return sqrt_price

    if add:
        liquidity = Decimal(liquidity).quantize(Decimal("1.0"))

        return liquidity * sqrt_price / (liquidity + amount_in * sqrt_price)
    else:
        return liquidity * sqrt_price / (liquidity - amount_in * sqrt_price)


def get_next_sqrt_price_from_amount1_rounding_down(sqrt_price, liquidity, amount_in, add):
    """
    Gets the next sqrt price given a delta of token1
    :param sqrt_price:
    :param liquidity:
    :param amount_in:
    :param add:
    :return:
    """
    if add:
        return (sqrt_price + amount_in / liquidity)
    else:
        return (sqrt_price - amount_in / liquidity)


def get_next_sqrt_price_from_input(sqrt_price:Decimal, liquidity:Decimal, amount_in:Decimal, zero_for_one):
    assert sqrt_price > 0
    assert liquidity > 0
    assert type(liquidity) is Decimal
    assert type(sqrt_price) is Decimal

    if zero_for_one:
        return get_next_sqrt_price_from_amount0_rounding_up(sqrt_price, liquidity, amount_in, True)

    return get_next_sqrt_price_from_amount1_rounding_down(sqrt_price, liquidity, amount_in, True)


def compute_swap_step(sqrt_price_current:Decimal, sqrt_price_target:Decimal, liquidity:Decimal, amount_remaining, feePips):
    # 对应v3 合约 computeSwapStep  函数。

    zero_for_one = sqrt_price_current >= sqrt_price_target
    # exactIn = amount_remaining >= 0

    amount_remaining_less_fee = Decimal( amount_remaining * Decimal(1 - feePips / 1e6)).quantize(Decimal("1.0"))
    print("sqrt_price_target",sqrt_price_target)
    print("sqrt_price_current",sqrt_price_current)
    amount_in = get_amount0_delta(sqrt_price_target,sqrt_price_current,liquidity,True) \
        if zero_for_one else get_amount1_delta(sqrt_price_target,sqrt_price_current,liquidity,True)
    print("amount in   预计算", amount_in)
    if amount_remaining_less_fee>= amount_in:
        print(" 不能在tick 内完成处理")
        sqrt_price_next = sqrt_price_target
    else:
        sqrt_price_next = get_next_sqrt_price_from_input(
            sqrt_price_current,
            liquidity,
            amount_remaining_less_fee,
            zero_for_one
        )
    max = (sqrt_price_next == sqrt_price_target)# 是否在space 处理完。
    print("sqrt_price_next is ", sqrt_price_next)
    print("需要跨space处理：", max)
    if zero_for_one:
        amount_in = amount_in if  max else get_amount0_delta(sqrt_price_next,sqrt_price_current,liquidity,True)
        amount_out = get_amount1_delta(sqrt_price_next,sqrt_price_current,liquidity,False)

    else:
        amount_in = amount_in if max else get_amount1_delta(sqrt_price_current,sqrt_price_next,liquidity,True)
        amount_out = get_amount0_delta(sqrt_price_current,sqrt_price_next,liquidity,False)


    if not max :
        fee = amount_remaining - amount_in
    else:
        fee =(amount_in*Decimal(feePips/1e6)).quantize(Decimal("1"))
    return sqrt_price_next,amount_in,amount_out,fee


def next_liquidity_tick(tickSpacing, current_tick, zero_for_one: bool):
    if  zero_for_one:
        ###token0->token1, price goes low.
        if current_tick % tickSpacing == 0:
            return current_tick - tickSpacing
        else:
            return current_tick - current_tick % tickSpacing
    else:
        ### token1->token0, price goes high
        if current_tick % tickSpacing == 0:
            return current_tick + tickSpacing
        else:
            return current_tick + (tickSpacing - current_tick % tickSpacing)