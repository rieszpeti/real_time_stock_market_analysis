import aiohttp
import logging
from urllib.parse import urlencode

from typing import Dict
from datetime import datetime

from ..models.stock_data import StockData, MetaData, StockDataMonthly


class StockDataFetcher:
    """Service class for fetching stock data from Alphavantage API."""

    def __init__(self, token: str):
        self.token = token
        self.logger = logging.getLogger(self.__class__.__name__)

    def map_response(self, json_response: Dict) -> StockDataMonthly | None:
        """Map the response from AlphaVantage API into the StockDataMonthly model."""
        if 'Time Series (1min)' not in json_response:
            return None

        time_series = json_response['Time Series (1min)']
        time_series_data = {}

        for timestamp_str, time_data in time_series.items():
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            stock_data = StockData(
                open=float(time_data['1. open']),
                high=float(time_data['2. high']),
                low=float(time_data['3. low']),
                close=float(time_data['4. close']),
                volume=int(time_data['5. volume'])
            )
            time_series_data[timestamp] = stock_data

        meta_data = MetaData(
            information=json_response['Meta Data']['1. Information'],
            symbol=json_response['Meta Data']['2. Symbol'],
            last_refreshed=json_response['Meta Data']['3. Last Refreshed'],
            interval=json_response['Meta Data']['4. Interval'],
            output_size=json_response['Meta Data']['5. Output Size'],
            time_zone=json_response['Meta Data']['6. Time Zone']
        )

        return StockDataMonthly(meta_data=meta_data, time_series=time_series_data)

    async def fetch_stock_data(self, symbol: str, specific_date: datetime) -> StockDataMonthly | None:
        """Fetch stock data for a symbol from AlphaVantage API."""
        specific_date_str = specific_date.strftime('%Y-%m')

        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": "1min",
            "date": specific_date_str,
            "outputsize": "full",
            "apikey": self.token
        }

        url = f"https://www.alphavantage.co/query?{urlencode(params)}"

        self.logger.info(f"Fetching stock data for symbol: {symbol} from {specific_date}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    self.logger.info(f"Fetched data for {symbol} for date: {specific_date}")
                    return self.map_response(data)
        except aiohttp.ClientError as e:
            self.logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None