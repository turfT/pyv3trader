from datetime import datetime, timedelta
import os
import time
import pyv3trader.utils.consant as constant


def download_bigquery_pool_event_matic(contract_address: str, date_begin: datetime, date_end: datetime,
                                       data_save_path: os.path):
    # iter date=> call download one day => save to date by date.
    contract_address = contract_address.lower()
    date_generated = [date_begin + timedelta(days=x) for x in range(0, (date_end - date_begin).days)]
    for one_day in date_generated:
        time_start = time.time()
        df = download_bigquery_pool_event_matic_oneday(contract_address, one_day)
        date_str = one_day.strftime("%Y-%m-%d")
        file_name = f"{contract_address}-{date_str}.csv"
        df.to_csv(data_save_path + "//" + file_name, header=True, index=False)
        time_end = time.time()
        print('Day: {}, time cost {} s, data count: {}'.format(date_str, time_end - time_start, len(df.index)))


def download_bigquery_pool_event_matic_oneday(contract_address, one_date):
    from google.cloud import bigquery
    client = bigquery.Client()
    query = f"""
select pool.block_number, pool.transaction_hash, pool.block_timestamp, pool.topics as pool_topics, 
pool.DATA as pool_data,  proxy.topics as proxy_topics,
pool.transaction_index as pool_tx_index, pool.log_index as pool_log_index from
(SELECT block_number,transaction_hash,block_timestamp,transaction_index,log_index,topics,DATA FROM
        public-data-finance.crypto_polygon.logs
        WHERE topics[SAFE_OFFSET(0)] in ('{constant.MINT_KECCAK}','{constant.BURN_KECCAK}','{constant.SWAP_KECCAK}')
            AND DATE(block_timestamp) >=  DATE("{one_date}")
            AND DATE(block_timestamp) <=  DATE("{one_date}")
            AND address = "{contract_address}" ) as pool
left join 
(SELECT transaction_hash,topics FROM public-data-finance.crypto_polygon.logs
        WHERE topics[SAFE_OFFSET(0)] in ('{constant.INCREASE_LIQUIDITY}','{constant.DECREASE_LIQUIDITY}')
            AND DATE(block_timestamp) >=  DATE("{one_date}")
            AND DATE(block_timestamp) <=  DATE("{one_date}")
            AND address = "{constant.PROXY_CONTRACT_ADDRESS}" ) as proxy
on pool.transaction_hash=proxy.transaction_hash order by pool.block_number asc
"""
    query_job = client.query(query)  # Make an API request.
    result = query_job.to_dataframe(create_bqstorage_client=False)
    return result
