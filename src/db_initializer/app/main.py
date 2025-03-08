import asyncio
import logging

from app.configs.config import load_general_config, load_secret_config, setup_logging
from app.services.sentiment_uploader import SentimentUploader
from app.services.stock_data_repository import StockDataRepository
from app.services.abstract_dbinitializer import AbstractDbInitializer
from app.services.dbinitializer_factory import DBInitializeType, DBInitializerFactory


async def main() -> None:
    setup_logging()
    logger = logging.getLogger("Main")
    logger.info("Starting Stock Data Publisher...")

    general_config = load_general_config()
    secrets_config = load_secret_config()

    repository = StockDataRepository(secrets_config.questdb_connection_str)
    await repository.create_tables()

    sentiment_repo = SentimentUploader(connection_string=secrets_config.postgres_connection_string)
    await sentiment_repo.create_tables()

    await sentiment_repo.upload_json()

    db_initialization_type: DBInitializeType = (
        DBInitializeType.FETCH_API
        if secrets_config.alphavantage_token == "EMPTY"
        else DBInitializeType.RANDOM_DATA
    )
        
    service: AbstractDbInitializer = DBInitializerFactory.get_db_initializer(
        db_initialization_type,
        secrets_config,
        general_config,
        repository
    )

    await service.initialize()


if __name__ == "__main__":
    asyncio.run(main())
