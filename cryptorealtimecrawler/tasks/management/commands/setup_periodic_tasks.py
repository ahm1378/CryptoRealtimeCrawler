from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import get_default_timezone_name
from django_celery_beat.models import IntervalSchedule, CrontabSchedule, PeriodicTask


from cryptorealtimecrawler.exchange_webservice.tasks import get_tf_coins_data, get_real_time_data, \
    get_five_min_data, get_fifteen_min_data, get_one_hour_data, \
    get_four_hour_data, get_daily_data, get_weekly_data



class Command(BaseCommand):
    help = """
    Setup celery beat periodic tasks.

    Following tasks will be created:

        - ....
    """

    @transaction.atomic
    def handle(self, *args, **kwargs):
        print('Deleting all periodic tasks and schedules...\n')

        IntervalSchedule.objects.all().delete()
        CrontabSchedule.objects.all().delete()
        PeriodicTask.objects.all().delete()

        """
        Example:
        {
            'task': periodic_task_name,
            'name': 'Periodic task description',
            # Everyday at 15:45
            # https://crontab.guru/#45_15_*_*_*
            'cron': {
                'minute': '45',
                'hour': '15',
                'day_of_week': '*',
                'day_of_month': '*',
                'month_of_year': '*',
            },
            'enabled': True
        },
        """
        periodic_tasks_data = [

            {
                'task': get_tf_coins_data,
                'name': 'Get TF coins data',
                'cron': {
                    'minute': '0',
                    'hour': '*/12',
                    'day_of_week': '*',
                    'day_of_month': '*',
                    'month_of_year': '*',
                },
                'enabled': True
            },
            {
                'task': get_real_time_data,
                'name': 'Get real-time data',
                'cron': {
                    'minute': '*/1',
                    'hour': '*',
                    'day_of_week': '*',
                    'day_of_month': '*',
                    'month_of_year': '*',
                },
                'enabled': True
            },
            {
                'task': get_five_min_data,
                'name': 'Get five minutes data',
                'cron': {
                    'minute': '*/7',
                    'hour': '*',
                    'day_of_week': '*',
                    'day_of_month': '*',
                    'month_of_year': '*',
                },
                'enabled': True
            },
            {
                'task': get_fifteen_min_data,
                'name': 'Run every 15 minutes',
                'cron': {
                    'minute': '*/15',
                    'hour': '*',
                    'day_of_week': '*',
                    'day_of_month': '*',
                    'month_of_year': '*',
                },
                'enabled': True
            },
            {
                'task': get_one_hour_data,
                'name': 'Run every hour',
                'cron': {
                    'minute': '45',
                    'hour': '*/1',
                    'day_of_week': '*',
                    'day_of_month': '*',
                    'month_of_year': '*',
                },
                'enabled': True
            },
            {
                'task': get_four_hour_data,
                'name': 'Run every 4 hours',
                'cron': {
                    'minute': '55',
                    'hour': '*/1',
                    'day_of_week': '*',
                    'day_of_month': '*',
                    'month_of_year': '*',
                },
                'enabled': True
            },
            {
                'task': get_daily_data,
                'name': 'Run daily',
                'cron': {
                    'minute': '55',
                    'hour': '*/1',
                    'day_of_week': '*',
                    'day_of_month': '*',
                    'month_of_year': '*',
                },
                'enabled': True
            },
            {
                'task': get_weekly_data,
                'name': 'Run weekly',
                'cron': {
                    'minute': '2',
                    'hour': '0',
                    'day_of_week': '0',
                    'day_of_month': '*',
                    'month_of_year': '*',
                },
                'enabled': True
            },
            # {
            #     'task': get_tradingview_idea_task,
            #     'name': 'tradingview_idea_task',
            #     'cron': {
            #         'minute': '0',
            #         'hour': '*/3',
            #         'day_of_week': '*',
            #         'day_of_month': '*',
            #         'month_of_year': '*',
            #     },
            #     'enabled': True
            # },
            # {
            #     'task': get_alpaca_news_task,
            #     'name': 'alpaca_news_task',
            #     'cron': {
            #         'minute': '10',
            #         'hour': '*/12',
            #         'day_of_week': '*',
            #         'day_of_month': '*',
            #         'month_of_year': '*',
            #     },
            #     'enabled': True
            # },
            # {
            #     'task': get_ddgs_news,
            #     'name': 'ddgs_news_task',
            #     'cron': {
            #         'minute': '20',
            #         'hour': '*/6',
            #         'day_of_week': '*',
            #         'day_of_month': '*',
            #         'month_of_year': '*',
            #     },
            #     'enabled': True
            # }

        ]

        timezone = get_default_timezone_name()

        for periodic_task in periodic_tasks_data:
            print(f'Setting up {periodic_task["task"].name}')

            cron = CrontabSchedule.objects.create(
                timezone=timezone,
                **periodic_task['cron']
            )

            PeriodicTask.objects.create(
                name=periodic_task['name'],
                task=periodic_task['task'].name,
                crontab=cron,
                enabled=periodic_task['enabled']
            )
