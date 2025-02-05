import time
from dataclasses import dataclass
from datetime import datetime, timezone

"""
I could have use Pydantic, but to keep it simple I added custom validation.

Other perspective would be to create a separate validator class,
but for this small project I didn't see the point of it.
"""

@dataclass
class StockData:
    symbol: str
    current: float  # Current price (c)
    open: float  # Open price of the day (o)
    high: float     # High price of the day (h)
    low: float      # Low price of the day (l)
    close: float  # Previous close price (pc)
    volume: float | None # finnhub does not include this
    timestamp: int = int(time.time() * 1e6)

    def __post_init__(self):
        if any(v is None for v in
               [self.symbol,
                self.current,
                self.high,
                self.low,
                self.open,
                self.close]):
            raise ValueError("None of the stock data values can be None.")


@dataclass
class StockDataMessage:
    symbol: str
    open: float  # This will be the current price
    high: float
    low: float
    close: float
    volume: int | None
    timestamp: int

    @classmethod
    def from_stock_data(cls, stock_data: StockData) -> "StockDataMessage":
        return cls(
            symbol=stock_data.symbol,
            open=stock_data.open,
            high=stock_data.high,
            low=stock_data.low,
            close=stock_data.close,
            volume=stock_data.volume,
            timestamp=stock_data.timestamp
        )