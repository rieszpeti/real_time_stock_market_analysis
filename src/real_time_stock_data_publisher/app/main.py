import asyncio
import logging

from app.configs.config import load_general_config, load_secret_config, setup_logging
from app.services.kafka_services import KafkaProducerService, StockDataPublisher
from app.services.rand_stock_data_generator import RandomStockDataGenerator
from app.services.stock_data_fetcher import StockDataFetcher

async def main() -> None:
    setup_logging()
    logger = logging.getLogger("Main")
    logger.info("Starting Stock Data Publisher...")

    secret_config = load_secret_config()
    general_config = load_general_config()

    # Create services
    stock_data_fetcher = StockDataFetcher(secret_config.finnhub_token)
    kafka_producer_service = KafkaProducerService(secret_config.kafka_producer_url)
    stock_data_publisher = StockDataPublisher(stock_data_fetcher, kafka_producer_service)

    logger.info(f"Configured to fetch and publish data for symbols: {', '.join(general_config.symbols)}")

    random_data_generator = None
    if secret_config.finnhub_token == "EMPTY":
        random_data_generator = RandomStockDataGenerator(general_config.symbols, kafka_producer_service)

    try:
        while True:
            if secret_config.finnhub_token == "EMPTY":
                if random_data_generator:
                    await random_data_generator.publish_random_stock_data()
            else:
                await stock_data_publisher.publish_stock_data(general_config.symbols)
            await asyncio.sleep(5)
    except KeyboardInterrupt:
        logger.info("Shutting down Stock Data Publisher.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


if __name__ == '__main__':
   asyncio.run(main())
