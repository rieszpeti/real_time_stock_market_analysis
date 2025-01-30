import json
import logging
import asyncio

from typing import List, Optional
from confluent_kafka import Producer

class KafkaProducerService:
    """Service class for producing messages to Kafka asynchronously."""
    
    def __init__(self, bootstrap_servers: str):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})
        self.logger = logging.getLogger(self.__class__.__name__)

    async def produce_message(self, topic: str, message: str) -> None:
        """Produce message to Kafka asynchronously."""
        await asyncio.to_thread(self._produce_message, topic, message)

    def _produce_message(self, topic: str, message: str) -> None:
        """Blocking call for Kafka produce message."""
        self.logger.info(f"Producing message to topic: {topic}")
        self.producer.produce(topic=topic, value=message, callback=self.delivery_report)
        self.producer.flush()

    def delivery_report(self, err: Optional[Exception], msg) -> None:
        """Callback function for Kafka delivery."""
        if err is not None:
            self.logger.error(f"Message delivery failed: {err}")
        else:
            self.logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

class StockDataPublisher:
    """Service class for fetching stock data and publishing it to Kafka asynchronously."""
    
    def __init__(self, stock_data_fetcher, kafka_producer_service):
        self.stock_data_fetcher = stock_data_fetcher
        self.kafka_producer_service = kafka_producer_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def publish_stock_data(self, symbols: List[str]) -> None:
        if symbols:
            for symbol in symbols:
                self.logger.info(f"Publishing stock data for symbol: {symbol}")
                stock_data = await self.stock_data_fetcher.fetch_stock_data(symbol)

                if stock_data is not None:
                    json_data = json.dumps(stock_data.__dict__)
                    topic = f"topic_{symbol}"

                    await self.kafka_producer_service.produce_message(topic, json_data)
                    self.logger.info(f"Published stock data for {symbol}: {json_data}")
                else:
                    self.logger.warning(f"Failed to fetch data for {symbol}")
        else:
            self.logger.warning(f"No symbols to publish.")