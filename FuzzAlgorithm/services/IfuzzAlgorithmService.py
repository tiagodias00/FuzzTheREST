from abc import ABC, abstractmethod


class IFuzzingService(ABC):
    @abstractmethod
    async def fuzz(self, data: dict):
        pass
