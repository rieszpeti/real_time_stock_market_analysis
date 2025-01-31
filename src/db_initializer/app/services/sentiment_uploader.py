import os
import json
import time
import logging
import asyncio
import asyncpg

from typing import AsyncGenerator
from datetime import datetime
from pathlib import Path


# Separate "Repository" part from the file reader these are two different classes
# Not a nice pattern to rethrow the exceptions and I quite like result pattern
# but due to the short period of time it was the quickest solution
class SentimentUploader:
    def __init__(
            self,
            connection_string: str = None
    ):
        self.connection_string = connection_string
        self.resources_folder = self._setup_resource_folder()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _setup_resource_folder(self) -> Path:
        real_path = os.path.realpath(__file__)
        return Path(real_path).parent.parent / "resources/sentiment"

    async def create_tables(self):
        """
            Idempotent script to create tables.
        """
        conn = None
        try:
            conn = await asyncpg.connect(self.connection_string)
            await conn.execute(f"""
                   CREATE TABLE IF NOT EXISTS sentiment_data (
                       file_name TEXT PRIMARY KEY,
                       content JSONB NOT NULL,
                       uploaded_at TIMESTAMPTZ NOT NULL
                   )
               """)
            self.logger.info(f"sentiment_data table created successfully.")
            await conn.close()
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise
        finally:
            if conn and not conn.is_closed():
                await conn.close()

    async def _is_file_uploaded(self, file_name: str) -> bool:
        """Check if file exists in the single table"""
        conn = None
        try:
            conn = await asyncpg.connect(self.connection_string)
            result = await conn.fetchval(
                f"SELECT 1 FROM sentiment_data WHERE file_name = $1",
                file_name
            )
            await conn.close()
            return bool(result)
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise
        finally:
            if conn and not conn.is_closed():
                await conn.close()

    async def _process_file(self, json_file: Path):
        """Process individual JSON file using async operations"""
        conn = None
        try:
            content = await asyncio.to_thread(self._read_json_file, json_file)
            conn = await asyncpg.connect(self.connection_string)
            await conn.execute(
                f"""
                    INSERT INTO sentiment_data (file_name, content, uploaded_at)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (file_name) DO NOTHING
                """,
                json_file.name,
                json.dumps(content),
                datetime.now()
            )
            self.logger.info(f"Successfully uploaded {json_file.name}")
            await conn.close()
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {json_file.name}: {e}")
            raise
        except asyncpg.PostgresError as e:
            self.logger.error(f"Database error processing {json_file.name}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error processing {json_file.name}: {e}")
            raise
        finally:
            if conn and not conn.is_closed():
                await conn.close()

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

    async def upload_json(self, max_retries: int = 5, backoff_factor: float = 2.0):
        """Main entry point for uploading JSON files"""
        for attempt in range(max_retries):
            try:
                async for json_file in self._load_json_files():
                    await self._process_file(json_file)
            except Exception as e:
                self.logger.error(f"Upload failed: {e}")
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** attempt
                    self.logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)  # Exponential backoff
                else:
                    self.logger.error("Max retries reached. Could not create sink.")