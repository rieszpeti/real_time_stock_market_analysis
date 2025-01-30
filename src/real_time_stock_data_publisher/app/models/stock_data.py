import time
from dataclasses import dataclass

"""
I could have use Pydantic, but to keep it simple I added custom validation.

Other perspective would be to create a separate validator class,
but for this small project I didn't see the point of it.
"""

@dataclass
class StockData:
    current: float  # Current price (c)
    open: float  # Open price of the day (o)
    high: float     # High price of the day (h)
    low: float      # Low price of the day (l)
    close: float  # Previous close price (pc)
    volume: float | None # finnhub does not include this
    timestamp: int = int(time.time() * 1000)

    def __post_init__(self):
        if any(v is None for v in
               [self.current,
                self.high,
                self.low,
                self.open,
                self.close]):
            raise ValueError("None of the stock data values can be None.")


