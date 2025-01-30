import logging
import asyncpg
from datetime import datetime

from ..models.stock_data import StockDataMonthly


class StockDataRepository:
    """Repository class for managing stock data in QuestDB."""

    def __init__(self, questdb_connection_str: str):
        self.questdb_connection_str = questdb_connection_str
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_tables(self) -> None:
        conn = None
        try:
            conn = await asyncpg.connect(dsn=self.questdb_connection_str)
            command = """
                CREATE TABLE IF NOT EXISTS stock_data (
                    symbol SYMBOL,        
                    open DOUBLE,             
                    high DOUBLE,            
                    low DOUBLE,                 
                    close DOUBLE,                
                    volume LONG,                    
                    timestamp TIMESTAMP
                ) 
                TIMESTAMP(timestamp)                 
                PARTITION BY YEAR
                DEDUP UPSERT KEYS(timestamp, symbol);
                """
            await conn.execute(command)
            self.logger.info("Table 'stock_data' created successfully.")
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
        finally:
            if conn:
                await conn.close()

    async def get_last_symbol_date(self, symbol: str) -> datetime | None:
        """Fetch the last date for which data is available for a symbol."""
        conn = None
        try:
            conn = await asyncpg.connect(dsn=self.questdb_connection_str)
            query = "SELECT MAX(timestamp) FROM stock_data WHERE symbol = $1"
            result = await conn.fetchval(query, symbol)
            await conn.close()
            return result if result else None
        except Exception as e:
            self.logger.error(f"Error fetching last symbol date for {symbol}: {e}")
            return None
        finally:
            if conn:
                await conn.close()

    async def insert_stock_data(self, stock_data: StockDataMonthly) -> None:
        """Insert fetched stock data into QuestDB."""
        conn = None
        try:
            conn = await asyncpg.connect(dsn=self.questdb_connection_str)

            for timestamp, data in stock_data.time_series.items():
                query = """
                    INSERT INTO stock_data (
                        symbol, 
                        open, 
                        high, 
                        low, 
                        close, 
                        volume, 
                        timestamp
                    )
                    VALUES 
                        ($1, $2, $3, $4, $5, $6, $7)
                """
                await conn.execute(
                    query,
                    stock_data.meta_data.symbol,
                    data.open,
                    data.high,
                    data.low,
                    data.close,
                    data.volume,
                    timestamp
                )

            await conn.close()
        except Exception as e:
            self.logger.error(f"Error inserting data into QuestDB: {e}")
        finally:
            if conn:
                await conn.close()

    async def is_data_already_inserted(self, symbol: str, timestamp: datetime) -> bool:
        """Check if stock data for the symbol and timestamp already exists in the database."""
        conn = None
        try:
            conn = await asyncpg.connect(dsn=self.questdb_connection_str)
            query = """
                SELECT 1 FROM stock_data
                WHERE symbol = $1 AND timestamp = $2
                LIMIT 1
            """
            result = await conn.fetchval(query, symbol, timestamp)
            await conn.close()
            return result is not None
        except Exception as e:
            self.logger.error(f"Error checking for duplicate data for {symbol} at {timestamp}: {e}")
            return False
        finally:
            if conn:
                await conn.close()