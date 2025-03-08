import os
import logging

import aiohttp
from typing import AsyncGenerator
from pathlib import Path

from .abstract_dbinitializer import AbstractDbInitializer


class StockDataUploader(AbstractDbInitializer):
    """Class responsible for reading stock data from csv files and uploading it to the database."""

    def __init__(self, url: str):
        self.url = url
        self.resources_folder = self._setup_resource_folder()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def _upload_data(self) -> None:
        """Uploads CSV files to the database asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async for csv_path in self._load_csv_files():
                    await self._upload_csv(session, csv_path)
        except Exception as e:
            self.logger.error(f"Error during upload process: {e}")

    def _setup_resource_folder(self) -> Path:
        real_path = os.path.realpath(__file__)
        resource_path = Path(real_path).parent.parent / "resources/stock_prices"
        return resource_path

    async def _load_csv_files(self) -> AsyncGenerator[Path, None]:
        """Asynchronously yields CSV file paths from the resources folder."""
        try:
            resources_path: Path = Path(self.resources_folder)
            for csv_file in resources_path.glob("*.csv"):
                yield csv_file
        except Exception as e:
            self.logger.error(f"Error loading CSV files from {self.resources_folder}: {e}")

    async def _upload_csv(self, session: aiohttp.ClientSession, csv_path: Path) -> None:
        """Uploads a single CSV file asynchronously."""
        try:
            with open(csv_path, 'rb') as file:
                data = {'data': file}
                async with session.post(self.url, data=data) as response:
                    response_text = await response.text()
                    if response.status == 200:
                        self.logger.info(f"Successfully uploaded {csv_path.name}")
                    else:
                        self.logger.error(
                            f"Failed to upload {csv_path.name}: {response.status} - {response_text}"
                        )
        except Exception as e:
            self.logger.error(f"Error uploading {csv_path.name}: {e}")

    async def initialize(self) -> None:
        await self._upload_data()