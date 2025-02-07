import asyncio
import os
import hashlib
import logging
import time
import asyncpg
import pytest
import requests
import pandas as pd

from pathlib import Path

from pandas import DataFrame
from pandas.testing import assert_frame_equal
from testcontainers.core.container import DockerContainer
from app.services.csv_uploader import StockDataUploader

logging.basicConfig(level=logging.INFO)

"""
https://stackoverflow.com/questions/76608690/pytest-best-practice-to-setup-and-teardown-before-and-after-all-tests

When there is a need for setup and teardown, 
I prefer implementing the test methods inside a Python class for better organization. 
In the following example, we have:

2 test methods test_sample_1 and test_sample_2
A method setup_class which gets invoked before all tests are invoked
A method teardown_class which gets invoked after all tests have been invoked
A method setup_method which gets invoked before each test is invoked
A method teardown_method which gets invoked after each test is invoked

I like this way too.
"""

class TestInitialization:
    _connection_string: str | None
    _rest_url: str | None
    _container: DockerContainer

    @classmethod
    def setup_class(cls):
        inner_quest_rest_port = 9000
        inner_quest_postgres_port = 8812
        inner_health_check_port = 9003

        cls._container = DockerContainer("questdb/questdb:latest")

        cls._container.with_exposed_ports(
            inner_quest_rest_port,
            inner_quest_postgres_port,
            inner_health_check_port
        ).with_env("QDB_DEBUG", "true") \
         .with_env("QDB_METRICS_ENABLED", "TRUE") \
         .with_env("QDB_LINE_TCP_WRITER_WORKER_COUNT", "1") \
         .with_env("JAVA_OPTS", "-Djava.locale.providers=JRE,SPI")

        cls._container.start()

        outer_quest_http_port = cls._container.get_exposed_port(inner_quest_rest_port)
        outer_quest_postgres_port = cls._container.get_exposed_port(inner_quest_postgres_port)
        outer_health_check_port = cls._container.get_exposed_port(inner_health_check_port)

        cls._connection_string = f"postgres://admin:quest@localhost:{outer_quest_postgres_port}/qdb"
        cls._rest_url = f"http://localhost:{outer_quest_http_port}/imp?name=stock_data"

        start_time = time.time()
        timeout = 30
        while True:
            try:
                response = requests.get(f"http://localhost:{outer_health_check_port}")
                if response.status_code < 500:
                    break
            except requests.exceptions.ConnectionError:
                pass

            if time.time() - start_time > timeout:
                raise RuntimeError("QuestDB container failed to start in time")
            time.sleep(0.5)
        pass

    @classmethod
    def teardown_class(cls):
        if not cls._container:
            cls._container.stop()
        pass

    def _get_resource_path(self) -> Path:
        real_path = os.path.realpath(__file__)
        parent_dir = Path(real_path).parent.parent
        resource_path = Path(parent_dir) / "app/resources/stock_prices/"
        return resource_path

    def _apply_data_transformation_rules(self, df: DataFrame) -> None:
        df.drop_duplicates(inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        df.sort_values(by=["symbol", "timestamp"], inplace=True)

    def _create_df_from_csvs(self, csv_dir: Path) -> pd.DataFrame:
        """Creates a combined DataFrame from all CSV files in a directory."""
        combined_data = []

        for file in sorted(Path(csv_dir).glob("*.csv")):
            df = pd.read_csv(file)
            combined_data.append(df)

        combined_df = pd.concat(combined_data, ignore_index=True)

        # symbol,open,high,low,close,volume,timestamp
        self._apply_data_transformation_rules(combined_df)

        return combined_df

    async def _create_df_from_db(self) -> pd.DataFrame:
        """Fetches all stock data from the database and creates a DataFrame."""
        conn = await asyncpg.connect(self._connection_string)

        rows = await conn.fetch("SELECT * FROM stock_data")

        await conn.close()

        df = pd.DataFrame(
            rows,
            columns=["symbol", "open", "high", "low", "close", "volume", "timestamp"]
        )

        self._apply_data_transformation_rules(df)

        return df

    @pytest.mark.asyncio
    async def test_csv_vs_db(self):
        csv_dir = self._get_resource_path()

        # act
        stock_data_uploader = StockDataUploader(self._rest_url)
        await stock_data_uploader.upload_data()

        csv_df = self._create_df_from_csvs(csv_dir)
        db_df = await self._create_df_from_db()

        # Compare the two DataFrames by values
        assert_frame_equal(csv_df,db_df, check_dtype=False)
