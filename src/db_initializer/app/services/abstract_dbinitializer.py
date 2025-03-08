from abc import ABC, abstractmethod

class AbstractDbInitializer(ABC):

    @abstractmethod
    async def initialize(self) -> None:
        pass
