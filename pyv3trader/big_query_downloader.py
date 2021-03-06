import pandas as pd
from datetime import datetime, timedelta
import requests
import pickle
import importlib
from itertools import compress
import time
import os
import math
from enum import Enum

from pyv3trader.utils.consant import MINT_KECCAK, BURN_KECCAK, SWAP_KECCAK


def download_bigquery_pool_event_matic(contract_address,date_begin:datetime,date_end:datetime,block_start,data_save_path:os.path):
    #iter date=> call download one day => save to date by date.
    date_generated = [date_begin + timedelta(days=x) for x in range(0, (date_end - date_begin).days)]
    for one_day in date_generated:
        df = download_bigquery_pool_event_matic_oneday(contract_address,one_day,block_start)
        date_str = one_day.strftime("%Y-%m-%d")
        file_name = f"{contract_address}{date_str}.csv"
        df.to_csv(data_save_path+"//"+file_name,header=True,index=False)


def download_bigquery_pool_event_matic_oneday(contract_address,one_date,block_start = 0):
    from google.cloud import bigquery
    client = bigquery.Client()

    query = f"""SELECT
        block_number,
        transaction_hash,
        block_timestamp,
        transaction_index,
        log_index,
        topics,
        DATA

        FROM
        public-data-finance.crypto_polygon.logs
        WHERE
            (topics[SAFE_OFFSET(0)] = '{MINT_KECCAK}'
            OR topics[SAFE_OFFSET(0)] = '{BURN_KECCAK}'
            OR topics[SAFE_OFFSET(0)] = '{SWAP_KECCAK}')
            AND DATE(block_timestamp) >=  DATE("{one_date}")
            AND DATE(block_timestamp) <=  DATE("{one_date}")
            AND block_number          >=  {block_start}
            AND address = "{contract_address}" """
    query_job = client.query(query)  # Make an API request.
    result = query_job.to_dataframe(create_bqstorage_client=False)
    return result

