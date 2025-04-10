from celery import shared_task
from cryptorealtimecrawler.exchange_webservice.crawler.real_time import FiveMinuteCrawler, FifteenMinutesCrawler, \
    FourHourCrawler, DailyCrawler, WeeklyCrawler,OneHourCrawler, CoinHandler



@shared_task
def get_tf_coins_data():
    crawler = CoinHandler()
    crawler.get_save_cmc_chains_data()
    crawler.get_save_cmc_coins_data()
    crawler.get_save_tf_coins_data()


@shared_task
def get_real_time_data():
    crawler = CoinHandler()
    print("get real time data")
    summary = crawler.get_save_realtime_data()
    return summary


@shared_task
def get_five_min_data():
    crawler = FiveMinuteCrawler()
    summary = crawler.run_save_ohlcv_redis()
    return summary


@shared_task
def get_fifteen_min_data():
    crawler = FifteenMinutesCrawler()
    summary = crawler.run_save_ohlcv_redis()
    return summary


@shared_task
def get_one_hour_data():
    crawler = OneHourCrawler()
    summary = crawler.run_save_ohlcv_redis()
    return summary


@shared_task
def get_four_hour_data():
    crawler = FourHourCrawler()
    summary = crawler.run_save_ohlcv_redis()
    return summary


@shared_task
def get_daily_data():
    crawler = DailyCrawler()
    summary = crawler.run_save_ohlcv_redis()
    return summary


@shared_task
def get_weekly_data():
    crawler = WeeklyCrawler()
    summary = crawler.run_save_ohlcv_redis()
    return summary
