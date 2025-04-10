# CryptoRealTimeCrawler

A project for collecting cryptocurrency data from multiple exchanges including:
- BingX
- LBank
- XT

## Key Features
- Real-time market data collection from multiple exchanges
- Historical price storage in various timeframes (5min, 15min, 1h, 4h, daily)
- Cryptocurrency and exchange symbol management
- Comprehensive REST API
- Authentication and security
- Advanced filtering and search capabilities

## API Endpoints
- `/cryptos/`: Cryptocurrency management
- `/exchange-symbols/`: Exchange symbol management
- `/market-data/`: Market data
- `/historical-prices/`: Historical prices
- `/cmc-tags/`: CMC tags

## Project Setup

1- Complete cookiecutter workflow (recommendation: leave project_slug empty) and go inside the project
```
cd CryptoRealTimeCrawler
```

2- SetUp venv
```
virtualenv -p python3.10 venv
source venv/bin/activate
```

3- Install Dependencies
```
pip install -r requirements_dev.txt
pip install -r requirements.txt
```

4- Create your env
```
cp .env.example .env
```

5- Create tables
```
python manage.py migrate
```

6- Spin off docker compose
```
docker compose -f docker-compose.dev.yml up -d
```

7- Run the project
```
python manage.py runserver
```