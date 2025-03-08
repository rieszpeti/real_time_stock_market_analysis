from enum import Enum

from ..configs.config import GeneralConfig, SecretConfig
from .abstract_dbinitializer import AbstractDbInitializer
from .stock_data_fetcher import StockDataFetcher
from .stock_data_service import StockDataService
from .stock_data_repository import StockDataRepository
from .csv_uploader import StockDataUploader


class DBInitializeType(Enum):
    FETCH_API = "fetch"
    RANDOM_DATA = "random_data"

class DBInitializerFactory:
    @staticmethod
    def get_db_initializer(
        api_or_random_stock_data: DBInitializeType,
        secrets_config: SecretConfig,
        general_config: GeneralConfig,
        repository: StockDataRepository
    ) -> AbstractDbInitializer:
        if api_or_random_stock_data == DBInitializeType.RANDOM_DATA:
            stock_data_uploader = StockDataUploader(secrets_config.questdb_rest_url)
            return stock_data_uploader 
        
        elif api_or_random_stock_data == DBInitializeType.FETCH_API:
            fetcher = StockDataFetcher(secrets_config.alphavantage_token)
            service = StockDataService(
                fetcher, 
                repository,
                general_config.symbols,
                general_config.scrape_start_date
            )
            return service

        else:
            raise ValueError(f"Unsupported DBInitializeType: {api_or_random_stock_data}")