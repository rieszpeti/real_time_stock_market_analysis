from dataclasses import dataclass
from datetime import datetime
from typing import Dict

"""
I could have use Pydantic, but to keep it simple I added custom validation.

Other perspective would be to create a separate validator class,
but for this small project I didn't see the point of it.
"""

@dataclass
class StockData:
    open: float
    high: float
    low: float
    close: float
    volume: int

    def __post_init__(self):
        if any(v is None for v in
               [self.open,
                self.high,
                self.low,
                self.close,
                self.volume]):
            raise ValueError("None of the stock data values can be None.")


@dataclass
class MetaData:
    information: str
    symbol: str
    last_refreshed: str
    interval: str
    output_size: str
    time_zone: str

    def __post_init__(self):
        if any(v is None for v in
               [self.information,
                self.symbol,
                self.last_refreshed,
                self.interval,
                self.output_size,
                self.time_zone]):
            raise ValueError("None of the meta data values can be None.")


@dataclass
class StockDataMonthly:
    meta_data: MetaData
    time_series: Dict[datetime, StockData]

    def __post_init__(self):
        if self.meta_data is None:
            raise ValueError("Meta data cannot be None.")
        if self.time_series is None:
            raise ValueError("Time series cannot be None.")
        if not self.time_series:
            raise ValueError("Time series cannot be empty.")
        for timestamp, stock_data in self.time_series.items():
            if stock_data is None:
                raise ValueError(f"Stock data for timestamp {timestamp} cannot be None.")
            stock_data.__post_init__()