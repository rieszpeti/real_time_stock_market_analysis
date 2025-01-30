import json
import logging
import random

from typing import List

from .kafka_services import KafkaProducerService
from ..models.stock_data import StockData


class RandomStockDataGenerator:
    def __init__(self, symbols: List[str], kafka_producer_service: KafkaProducerService):
        self.symbols = symbols
        self.kafka_producer_service = kafka_producer_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def publish_random_stock_data(self) -> None:
        """Generate random stock data."""

        if self.symbols:
            for symbol in self.symbols:
                self.logger.info(f"Generating random stock data for symbol: {symbol}")
                try:
                    # Randomly generate stock data values
                    rand_stock_data = StockData(
                        open=random.uniform(100, 500),     # Open price between 100 and 500
                        current=random.uniform(100, 500),  # Current price between 100 and 500
                        high=random.uniform(100, 500),     # High price between 100 and 500
                        low=random.uniform(100, 500),      # Low price between 100 and 500
                        close=random.uniform(100, 500),    # Previous close price between 100 and 500
                        volume=random.uniform(100, 500)    # Volume price between 100 and 500
                    )

                    json_data = json.dumps(rand_stock_data.__dict__)
                    topic = f"topic_{symbol}"

                    await self.kafka_producer_service.produce_message(topic, json_data)
                    self.logger.info(f"Generated random data for {symbol}: {rand_stock_data}")
                except Exception as e:
                    self.logger.error(f"Error generating stock data for {symbol}: {e}")
        else:
            self.logger.warning(f"No symbols to publish.")


