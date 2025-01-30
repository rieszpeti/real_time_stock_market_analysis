import asyncio
import logging

from app.configs.config import load_general_config, load_secret_config, setup_logging
from app.services.csv_uploader import StockDataUploader
from app.services.sentiment_uploader import SentimentUploader
from app.services.stock_data_fetcher import StockDataFetcher
from app.services.stock_data_repository import StockDataRepository
from app.services.stock_data_service import StockDataService


async def main() -> None:
    setup_logging()
    logger = logging.getLogger("Main")
    logger.info("Starting Stock Data Publisher...")

    general_config = load_general_config()
    secrets_config = load_secret_config()

    repository = StockDataRepository(secrets_config.questdb_connection_str)
    await repository.create_tables()

    secrets_config.alphavantage_token = "EMPTY"

    sentiment_repo = SentimentUploader(connection_string=secrets_config.postgre_connection_string)

    await sentiment_repo.upload_json()

    if secrets_config.alphavantage_token == "EMPTY":
        stock_data_uploader = StockDataUploader(secrets_config.questdb_rest_url)
        await stock_data_uploader.upload_data()
    else:
        fetcher = StockDataFetcher(secrets_config.alphavantage_token,)
        service = StockDataService(fetcher, repository)

        await service.fetch_stock_data_from(general_config.symbols, general_config.scrape_start_date)


if __name__ == "__main__":
    asyncio.run(main())
