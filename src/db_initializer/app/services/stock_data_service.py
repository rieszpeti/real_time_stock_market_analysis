import logging

from datetime import datetime
from typing import List
from dateutil.relativedelta import relativedelta

from ..services.stock_data_fetcher import StockDataFetcher
from ..services.stock_data_repository import StockDataRepository


class StockDataService:
    """Service for orchestrating stock data fetching and insertion."""

    def __init__(
            self,
            fetcher: StockDataFetcher,
            repository: StockDataRepository
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.fetcher = fetcher
        self.repository = repository

    async def fetch_and_insert_stock_data(self, symbol: str, specific_date: datetime) -> None:
        """Fetch stock data for a symbol and insert it into the database."""
        last_symbol_date = await self.repository.get_last_symbol_date(symbol)

        if last_symbol_date and specific_date <= last_symbol_date:
            self.logger.info(f"Skipping data fetch for {symbol}, data already exists for {specific_date}.")
            return

        stock_data = await self.fetcher.fetch_stock_data(symbol, specific_date)
        if stock_data:
            for timestamp, data in stock_data.time_series.items():
                if await self.repository.is_data_already_inserted(symbol, timestamp):
                    self.logger.info(f"Data for {symbol} at {timestamp} already exists. Skipping.")
                else:
                    await self.repository.insert_stock_data(stock_data)
                    self.logger.info(f"Inserted data for {symbol} at {timestamp}")
        else:
            self.logger.error(f"No data fetched for {symbol}")

    async def fetch_stock_data_from(self, symbols: List[str], start_date: datetime) -> None:
        """Fetch and insert stock data for multiple symbols over a date range."""
        end_date = self.get_current_date()

        for symbol in symbols:
            delta = relativedelta(months=1)
            while start_date <= end_date:
                self.logger.info(f"Processing data for {symbol} for {start_date.strftime('%Y-%m')}")
                await self.fetch_and_insert_stock_data(symbol, start_date)
                start_date += delta

    def get_current_date(self) -> datetime:
        return datetime(datetime.today().year, datetime.today().month, 1)