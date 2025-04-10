# Generated by Django 4.0.7 on 2025-04-10 21:53

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CMCTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'cmc_tag',
            },
        ),
        migrations.CreateModel(
            name='Crypto',
            fields=[
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('full_name', models.CharField(max_length=255)),
                ('cmc_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('is_main', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'cryptocurrencies',
                'db_table': 'crypto',
            },
        ),
        migrations.CreateModel(
            name='OneHourPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('timestamp', models.BigIntegerField()),
                ('open', models.DecimalField(decimal_places=8, max_digits=30)),
                ('close', models.DecimalField(decimal_places=8, max_digits=30)),
                ('high', models.DecimalField(decimal_places=8, max_digits=30)),
                ('low', models.DecimalField(decimal_places=8, max_digits=30)),
                ('volume', models.DecimalField(decimal_places=8, max_digits=30)),
                ('indicators', models.JSONField(blank=True, null=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='exchange_webservice.crypto')),
            ],
            options={
                'db_table': 'one_hour_price',
            },
        ),
        migrations.CreateModel(
            name='FourHourPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('timestamp', models.BigIntegerField()),
                ('open', models.DecimalField(decimal_places=8, max_digits=30)),
                ('close', models.DecimalField(decimal_places=8, max_digits=30)),
                ('high', models.DecimalField(decimal_places=8, max_digits=30)),
                ('low', models.DecimalField(decimal_places=8, max_digits=30)),
                ('volume', models.DecimalField(decimal_places=8, max_digits=30)),
                ('indicators', models.JSONField(blank=True, null=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='exchange_webservice.crypto')),
            ],
            options={
                'db_table': 'four_hour_price',
            },
        ),
        migrations.CreateModel(
            name='FiveMinutePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('timestamp', models.BigIntegerField()),
                ('open', models.DecimalField(decimal_places=8, max_digits=30)),
                ('close', models.DecimalField(decimal_places=8, max_digits=30)),
                ('high', models.DecimalField(decimal_places=8, max_digits=30)),
                ('low', models.DecimalField(decimal_places=8, max_digits=30)),
                ('volume', models.DecimalField(decimal_places=8, max_digits=30)),
                ('indicators', models.JSONField(blank=True, null=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='exchange_webservice.crypto')),
            ],
            options={
                'db_table': 'five_minute_price',
            },
        ),
        migrations.CreateModel(
            name='FifteenMinutePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('timestamp', models.BigIntegerField()),
                ('open', models.DecimalField(decimal_places=8, max_digits=30)),
                ('close', models.DecimalField(decimal_places=8, max_digits=30)),
                ('high', models.DecimalField(decimal_places=8, max_digits=30)),
                ('low', models.DecimalField(decimal_places=8, max_digits=30)),
                ('volume', models.DecimalField(decimal_places=8, max_digits=30)),
                ('indicators', models.JSONField(blank=True, null=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='exchange_webservice.crypto')),
            ],
            options={
                'db_table': 'fifteen_minute_price',
            },
        ),
        migrations.CreateModel(
            name='ExchangeSymbol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('exchange', models.CharField(max_length=50)),
                ('symbol', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchange_symbols', to='exchange_webservice.crypto')),
            ],
            options={
                'db_table': 'exchange_symbol',
            },
        ),
        migrations.CreateModel(
            name='DailyPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('timestamp', models.BigIntegerField()),
                ('open', models.DecimalField(decimal_places=8, max_digits=30)),
                ('close', models.DecimalField(decimal_places=8, max_digits=30)),
                ('high', models.DecimalField(decimal_places=8, max_digits=30)),
                ('low', models.DecimalField(decimal_places=8, max_digits=30)),
                ('volume', models.DecimalField(decimal_places=8, max_digits=30)),
                ('indicators', models.JSONField(blank=True, null=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='exchange_webservice.crypto')),
            ],
            options={
                'db_table': 'daily_price',
            },
        ),
        migrations.CreateModel(
            name='CMCMarketData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cmc_rank', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('max_supply', models.DecimalField(decimal_places=8, max_digits=30, null=True)),
                ('circulating_supply', models.DecimalField(decimal_places=8, max_digits=30, null=True)),
                ('total_supply', models.DecimalField(decimal_places=8, max_digits=30, null=True)),
                ('infinite_supply', models.BooleanField(default=False)),
                ('num_market_pairs', models.IntegerField(default=0)),
                ('last_updated', models.DateTimeField()),
                ('crypto', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cmc_data', to='exchange_webservice.crypto')),
            ],
            options={
                'verbose_name': 'CMC Market Data',
                'db_table': 'cmc_market_data',
            },
        ),
        migrations.CreateModel(
            name='CMCCryptoTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cmc_tags', to='exchange_webservice.crypto')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange_webservice.cmctag')),
            ],
            options={
                'db_table': 'cmc_crypto_tag',
            },
        ),
        migrations.AddIndex(
            model_name='exchangesymbol',
            index=models.Index(fields=['exchange', 'symbol'], name='exchange_sy_exchang_e4d835_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='exchangesymbol',
            unique_together={('crypto', 'exchange')},
        ),
        migrations.AlterUniqueTogether(
            name='cmccryptotag',
            unique_together={('crypto', 'tag')},
        ),
    ]
