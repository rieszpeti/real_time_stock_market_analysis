import json
import logging
import os

from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import List

@dataclass
class GeneralConfig:
    symbols: List[str] = field(default_factory=list)
    message_config: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.symbols:
            raise ValueError("The 'symbols' field cannot be empty.")
        if not all(isinstance(symbol, str) for symbol in self.symbols):
            raise ValueError("All symbols must be strings.")
        if not self.message_config:
            raise ValueError("The 'message_config' field cannot be empty.")


@dataclass
class SecretConfig:
    finnhub_token: str = None
    kafka_producer_url: str = None
    kafka_sink_url: str = None

    def __post_init__(self):
        if self.finnhub_token is None or len(self.finnhub_token.strip()) == 0:
            raise ValueError("Finnhub token cannot be None or empty.")

        if self.kafka_producer_url is None or len(self.kafka_producer_url.strip()) == 0:
            raise ValueError("Kafka producer url cannot be None or empty.")

        if self.kafka_sink_url is None or len(self.kafka_sink_url.strip()) == 0:
            raise ValueError("Kafka sink url cannot be None or empty.")


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
        message_config = config_data['message_config']
        if not symbols:
            raise ValueError("Message config cannot be empty.")
    except KeyError:
        raise ValueError("The 'message_config' key is missing in the configuration file.")

    return GeneralConfig(
        symbols=symbols,
        message_config=message_config
    )


def load_secret_config() -> SecretConfig:
    load_dotenv()

    finnhub_token = os.getenv("FINNHUB_TOKEN", "EMPTY")
    if not finnhub_token:
        raise ValueError("The 'FINNHUB_TOKEN' environment variable is missing.")

    kafka_producer_url = os.getenv("KAFKA_PRODUCER_URL", "broker:29092")

    if not kafka_producer_url:
        raise ValueError("The 'KAFKA_PRODUCER_URL' environment variable is missing.")

    kafka_sink_url = os.getenv("KAFKA_SINK_BASE_URL", "http://kafka-connect:8083/connectors")

    if not kafka_sink_url:
        raise ValueError("The 'KAFKA_SINK_BASE_URL' environment variable is missing.")

    return SecretConfig(
        finnhub_token=finnhub_token,
        kafka_producer_url=kafka_producer_url,
        kafka_sink_url=kafka_sink_url
    )


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("stock_data_publisher.log", mode='a')
        ]
    )