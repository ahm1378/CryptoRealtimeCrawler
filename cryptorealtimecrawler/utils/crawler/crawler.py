import time

from pandas import DataFrame
import pandas as pd

def get_start_time(timeframe):

    timeframe_durations = {
        '5m': 5 * 60,
        '15m': 15 * 60,
        '1h': 60 * 60,
        '4h': 4 * 60 * 60
    }

    if timeframe not in timeframe_durations:
        raise ValueError("Invalid timeframe. Supported timeframes are: '5m', '15m', '1h', '4h'")

    current_time = int(time.time())

    duration = 1000 * timeframe_durations[timeframe]

    start_time = (current_time - duration) * 1000

    return start_time


def convert_ohlc_to_heikinashi(data:DataFrame):
    df_HA = data.copy()
    df_HA['Adj_Close'] = df_HA['Close']
    df_HA['Adj_Open'] = df_HA['Open']
    df_HA['Adj_High'] = df_HA['High']
    df_HA['Adj_Low'] = df_HA['Low']
    df_HA['Close'] = (df_HA['Open'] + df_HA['High'] + df_HA['Low'] + df_HA['Close']) / 4

    for i in range(0, len(df_HA)):
        if i == 0:
            df_HA['Open'][i] = ((df_HA['Open'][i] + df_HA['Close'][i]) / 2)
        else:
            df_HA['Open'][i] = ((df_HA['Open'][i - 1] + df_HA['Close'][i - 1]) / 2)

    df_HA['High'] = df_HA[['Open', 'Close', 'High']].max(axis=1)
    df_HA['Low'] = df_HA[['Open', 'Close', 'Low']].min(axis=1)
    return df_HA

