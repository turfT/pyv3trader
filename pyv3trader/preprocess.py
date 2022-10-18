import datetime
import glob
import os
import pandas as pd
import pyv3trader.utils.consant as constant


def decode_file_name(file_path, file_name: str) -> (str, datetime.date):
    temp_str = file_name.replace(file_path, "").replace(".csv", "").strip("/")
    date_str = temp_str[-10:]
    pool_address = temp_str[:-10]
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    return pool_address, date


def check_file(file_path, file_name, pool, start_date, end_date) -> bool:
    pool_address, date = decode_file_name(file_path, file_name)
    is_in = date > start_date and date < end_date
    return is_in and pool == pool_address


def merge_file(start_date, end_date, file_path, pool_address) -> pd.DataFrame:
    all_files = glob.glob(
        os.path.join(file_path, "*.csv"))  # advisable to use os.path.join as this makes concatenation OS independent

    wanted_files = [file for file in all_files if check_file(file_path, file, pool_address, start_date, end_date)]

    df_from_each_file = (pd.read_csv(f) for f in wanted_files)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
    return concatenated_df


def signed_int(h):
    """
    Converts hex values to signed integers.
    """
    s = bytes.fromhex(h[2:])
    i = int.from_bytes(s, 'big', signed=True)
    return i


def hex_to_address(topic_str):
    return "0x" + topic_str[26:]


def handle_proxy_event(topic_str):
    if topic_str is None:
        return None
    topic_list = topic_str.strip("[]").replace("'", "").replace(" ", "").split("\n")
    type_topic = topic_list[0]
    if len(topic_list) > 1 and (type_topic == constant.INCREASE_LIQUIDITY or type_topic == constant.DECREASE_LIQUIDITY):
        return int(topic_list[1], 16);
    else:
        return None


def handle_event(topics_str, data_hex):
    # proprocess topics string ->topic list
    # topics_str = topics.values[0]
    sqrtPriceX96 = receipt = amount1 = current_liquidity = current_tick = tick_lower = tick_upper = delta_liquidity = None
    topic_list = topics_str.strip("[]").replace("'", "").replace(" ", "").split("\n")

    # data_hex = data.values[0]

    type_topic = topic_list[0]
    tx_type = constant.type_dict[type_topic]
    no_0x_data = data_hex[2:]
    chunk_size = 64
    chunks = len(no_0x_data)

    if tx_type == constant.onchainTxType.SWAP:
        sender = hex_to_address(topic_list[1])
        receipt = hex_to_address(topic_list[2])
        split_data = ["0x" + no_0x_data[i:i + chunk_size] for i in range(0, chunks, chunk_size)]
        amount0, amount1, sqrtPriceX96, current_liquidity, current_tick = [signed_int(onedata) for onedata in
                                                                           split_data]

    elif tx_type == constant.onchainTxType.BURN:
        sender = hex_to_address(topic_list[1])
        tick_lower = signed_int(topic_list[2])
        tick_upper = signed_int(topic_list[3])
        split_data = ["0x" + no_0x_data[i:i + chunk_size] for i in range(0, chunks, chunk_size)]
        delta_liquidity, amount0, amount1 = [signed_int(onedata) for onedata in split_data]
        delta_liquidity = -delta_liquidity

    elif tx_type == constant.onchainTxType.MINT:
        # sender = topic_str_to_address(topic_list[1])
        owner = hex_to_address(topic_list[1])
        tick_lower = signed_int(topic_list[2])
        tick_upper = signed_int(topic_list[3])
        split_data = ["0x" + no_0x_data[i:i + chunk_size] for i in range(0, chunks, chunk_size)]
        sender = hex_to_address(split_data[0])
        delta_liquidity, amount0, amount1 = [signed_int(onedata) for onedata in split_data[1:]]


    else:
        raise ValueError("not support tx type")

    return tx_type.name, sender, receipt, amount0, amount1, sqrtPriceX96, current_liquidity, current_tick, tick_lower, tick_upper, delta_liquidity


def handle_tick(lower_tick, upper_tick, current_tick, delta):
    if lower_tick is None or upper_tick is None or current_tick is None:
        return 0
    if lower_tick < current_tick < upper_tick:
        return delta
    else:
        return 0


def preprocess(pool_address, start_date, end_date, data_file_path):
    # FIXME BUG: start == end。  merge fail
    df = merge_file(start_date, end_date, data_file_path, pool_address)

    return preprocess_one(df)


def preprocess_one(df):
    # FIXME BUG: start == end。  merge fail
    df[["tx_type", "sender", "receipt", "amount0", "amount1",
        "sqrtPriceX96", "current_liquidity", "current_tick", "tick_lower", "tick_upper", "delta_liquidity"]] = df.apply(
        lambda x: handle_event(x.pool_topics, x.pool_data), axis=1, result_type="expand")
    df["position_id"] = df.apply(lambda x: handle_proxy_event(x.proxy_topics), axis=1)
    df = df.drop(columns=["pool_topics", "pool_data", "proxy_topics"])
    df = df.sort_values(['block_number', 'pool_log_index'], ascending=[True, True])
    df[["sqrtPriceX96", "current_liquidity", "current_tick"]] = df[
        ["sqrtPriceX96", "current_liquidity", "current_tick"]].fillna(method="ffill")
    df["delta_liquidity"] = df["delta_liquidity"].fillna(0)
    df["delta_liquidity"] = df.apply(
        lambda x: handle_tick(x.tick_lower, x.tick_upper, x.current_tick, x.delta_liquidity), axis=1)
    df["current_liquidity"] = df["current_liquidity"] + df["delta_liquidity"]
    df["block_timestamp"] = df["block_timestamp"].apply(lambda x: x.split("+")[0])
    return df
