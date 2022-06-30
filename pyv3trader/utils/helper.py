import decimal
from decimal import Decimal
from typing import Union

from .types import AddressLike, Address
import json
import os
import math


def _str_to_addr(s: Union[AddressLike, str]) -> Address:
    """Idempotent"""
    if isinstance(s, str):
        if s.startswith("0x"):
            return Address(bytes.fromhex(s[2:]))
        else:
            raise Exception(f"Couldn't convert string '{s}' to AddressLike")
    else:
        return s


def _load_abi(name: str):
    path = f"{os.path.dirname(os.path.abspath(__file__))}/assets/"
    with open(os.path.abspath(path + f"{name}")) as f:
        abi = json.load(f)
    return abi["abi"]


def _x96_to_decimal(number: int):
    return Decimal(number) / 2 ** 96

def decimal_to_x96(number:Decimal):
    return int(Decimal(number) * 2 ** 96)

def _x96_sqrt_to_decimal(sqrt_priceX96,token_decimal_diff=12):
    price = _x96_to_decimal(sqrt_priceX96)
    return (price**2)/10**token_decimal_diff

## can round by spacing?
def sqrt_price_to_ticker(sqrt_priceX96:int)->int:
    decimal_price = _x96_to_decimal(sqrt_priceX96)
    return pool_price_to_ticker(decimal_price)

def pool_price_to_ticker(price_decimal:Decimal):
    return int(math.log(price_decimal, math.sqrt(1.0001)))


def ticker_to_sqrt_price_x96(ticker)->int:
    return  int(decimal_to_x96( Decimal((Decimal.sqrt(Decimal(1.0001))) ** ticker)))



def tick_to_usd_based_price(tick:int,token_0_decimal,token_1_decimal,token_0_is_usdlike:bool):
    sqrt_price = ticker_to_sqrt_price_x96(tick)
    decimal_price = _x96_to_decimal(sqrt_price) ** 2
    pool_price = decimal_price * Decimal(10 ** (token_0_decimal - token_1_decimal))
    return Decimal(1/pool_price) if token_0_is_usdlike else pool_price


def usd_based_price_to_tick(usd_based_price:Decimal,token_0_decimal,
                              token_1_decimal,token_0_is_usdlike)->int:
        #usd_based price->add decimal pool price->sqrt_price ->ticker

    pool_price = (1/usd_based_price if token_0_is_usdlike else usd_based_price )/\
                 Decimal(10**(token_0_decimal-token_1_decimal))
    decimal_price = Decimal.sqrt(pool_price)
    sqrt_price = decimal_to_x96(decimal_price)
    tick = sqrt_price_to_ticker(sqrt_price)
    return tick

def token_int_to_float(token_amt:int,decimal:int):
    return token_amt/10**decimal