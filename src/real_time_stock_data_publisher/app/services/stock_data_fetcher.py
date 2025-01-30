import aiohttp
import logging

from typing import Optional

from ..models.stock_data import StockData

class StockDataFetcher:
    """
        Service class for fetching stock data from Finnhub API asynchronously.
        30 API calls/ second limit

        https://api.alpaca.markets
    """
    
    def __init__(self, token: str):
        self.token = token
        self.logger = logging.getLogger(self.__class__.__name__)

    async def fetch_stock_data(self, symbol: str) -> Optional[StockData]:
        """Fetch stock data from Alpaca API."""
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.token}"
        self.logger.info(f"Fetching stock data for symbol: {symbol}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    self.logger.info(f"Fetched data for {symbol}: {data}")
                    return self.map_stock_data(data)
        except aiohttp.ClientError as e:
            self.logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None

    def map_stock_data(self, data: dict) -> StockData:
        """Maps raw API response data to StockData dataclass."""
        try:
            return StockData(
                open=data['o'],  # 'o' is the open price
                current=data['c'],  # 'c' is the current price
                high=data['h'],  # 'h' is the high price
                low=data['l'],  # 'l' is the low price
                close=data['pc'],  # 'pc' is the previous close price
                volume=None
            )
        except KeyError as e:
            self.logger.error(f"Missing expected field in data: {e}")
            raise ValueError(f"Invalid data received: {e}")