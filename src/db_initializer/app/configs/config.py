import json
import logging
import os

from pathlib import Path

from dotenv import load_dotenv
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class GeneralConfig:
    symbols: List[str] = field(default_factory=list)
    scrape_start_date: datetime = None

    def __post_init__(self):
        if not self.symbols:
            raise ValueError("The 'symbols' field cannot be empty.")
        if not all(isinstance(symbol, str) for symbol in self.symbols):
            raise ValueError("All symbols must be strings.")

        if not isinstance(self.scrape_start_date, datetime):
            raise ValueError("The 'scrape_start_date' must be a datetime object.")
        if self.scrape_start_date > datetime.now():
            raise ValueError("The 'scrape_start_date' cannot be in the future.")

@dataclass
class SecretConfig:
    alphavantage_token: str = None
    questdb_connection_str: str = None
    questdb_rest_url: str = None
    postgres_connection_string: str = None

    def __post_init__(self):
        if self.alphavantage_token is None or len(self.alphavantage_token.strip()) == 0:
            raise ValueError("Alphavantage token cannot be None or empty.")
        if self.questdb_rest_url is None or len(self.questdb_rest_url.strip()) == 0:
            raise ValueError("QuestDB Rest url cannot be None or empty.")


def load_general_config() -> GeneralConfig:
    real_path = os.path.realpath(__file__)
    config_path = Path(real_path).parent / "config.json"

    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"Configuration file '{config_path}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding JSON in '{config_path}'.")

    try:
        symbols = config_data['symbols']
        if not symbols:
            raise ValueError("Symbols list cannot be empty.")
    except KeyError:
        raise ValueError("The 'symbols' key is missing in the configuration file.")

    try:
        scrape_start_date = datetime.strptime(
            config_data['scrape_start_date'], '%Y-%m'
        )
    except KeyError:
        raise ValueError("The 'scrape_start_date' key is missing in the configuration file.")
    except ValueError:
        raise ValueError("The 'scrape_start_date' is not in the correct format (YYYY-MM).")

    return GeneralConfig(symbols=symbols, scrape_start_date=scrape_start_date)


def load_secret_config() -> SecretConfig:
    load_dotenv()

    alphavantage_token = os.getenv("ALPHAVANTAGE_TOKEN")

    questdb_connection_str = os.getenv(
        "QUESTDB_CONNECTION_STR",
        "postgres://admin:quest@questdb:8812/qdb"
    )

    questdb_rest_url = os.getenv(
        "QUESTDB_REST_URL",
        "http://questdb:9000/imp?name=stock_data"
    )

    postgres_connection_string = os.getenv(
        "POSTGRES_CONNECTION_STR",
        "postgresql://admin:admin@postgres:5432/sentiment"
    )

    return SecretConfig(
        alphavantage_token=alphavantage_token,
        questdb_connection_str=questdb_connection_str,
        questdb_rest_url=questdb_rest_url,
        postgres_connection_string=postgres_connection_string
    )


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("db_initializer.log", mode='a')
        ]
    )