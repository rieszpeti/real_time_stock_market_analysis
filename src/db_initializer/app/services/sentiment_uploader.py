import os
import json
import logging
import asyncio
from typing import AsyncGenerator

import asyncpg

from datetime import datetime
from pathlib import Path


class SentimentUploader:
    def __init__(
            self,
            connection_string: str = None,
            data_table: str = "sentiment_data"
    ):
        self.connection_string = connection_string
        self.data_table = data_table
        self.pool = None
        self.resources_folder = self._setup_resource_folder()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _setup_resource_folder(self) -> Path:
        real_path = os.path.realpath(__file__)
        return Path(real_path).parent.parent / "resources/sentiment"

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute(f"""
                   CREATE TABLE IF NOT EXISTS {self.data_table} (
                       file_name TEXT PRIMARY KEY,
                       content JSONB NOT NULL,
                       uploaded_at TIMESTAMPTZ NOT NULL
                   )
               """)

    async def connect(self):
        """Create PostgreSQL connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.connection_string,
                min_size=2,
                max_size=10
            )
            self.logger.info("Connected to PostgreSQL successfully")
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise

    async def _is_file_uploaded(self, file_name: str) -> bool:
        """Check if file exists in the single table"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                f"SELECT 1 FROM {self.data_table} WHERE file_name = $1",
                file_name
            )
            return bool(result)

    async def _process_file(self, json_file: Path):
        """Process individual JSON file using async operations"""
        try:
            content = await asyncio.to_thread(self._read_json_file, json_file)
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        f"INSERT INTO {self.data_table} (file_name, content, uploaded_at) VALUES ($1, $2, $3)",
                        json_file.name,
                        json.dumps(content),
                        datetime.now()
                    )
                    self.logger.info(f"Successfully uploaded {json_file.name}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {json_file.name}: {e}")
        except asyncpg.PostgresError as e:
            self.logger.error(f"Database error processing {json_file.name}: {e}")
        except Exception as e:
            self.logger.error(f"Error processing {json_file.name}: {e}")

    def _read_json_file(self, json_file: Path) -> dict:
        with open(json_file, 'r') as f:
            return json.load(f)

    async def _load_json_files(self) -> AsyncGenerator[Path, None]:
        """Async file discovery with metadata check"""
        try:
            resources_path = Path(self.resources_folder)
            for json_file in resources_path.glob("*.json"):
                if not await self._is_file_uploaded(json_file.name):
                    yield json_file
                else:
                    self.logger.info(f"Skipping already uploaded: {json_file.name}")
        except Exception as e:
            self.logger.error(f"File loading error: {e}")
            raise

    async def upload_json(self):
        """Main entry point for uploading JSON files"""
        try:
            await self.connect()
            await self.create_tables()
            async for json_file in self._load_json_files():
                await self._process_file(json_file)
        except Exception as e:
            self.logger.error(f"Upload failed: {e}")
        finally:
            if self.pool:
                await self.pool.close()