from enum import Enum


class Coin_REDIS_KEY(Enum):
    FIVE_MINUTE = "FiveMinuteData"
    FIFTEEN_MINUTES = "FifteenMinutesData"
    ONE_HOUR = "OneHourData"
    FOUR_HOUR = "FourHourData"
    DAILY = "DailyData"
    WEEKLY = "WeeklyData"
    REAL_TIME_DATA = "RealTimeData"
    ORDER_BOOK_DATA = "OrderBookData"
    CMC_COINS_DATA = "CMCCoinsData"
    CMC_CHAINS_DATA = "CMCChainsData"
    CHAINS_TVL_Percentages = "ChainsTVLPercentages"
    TOTAL_TVL_DATA = "TotalTVLData"
    

