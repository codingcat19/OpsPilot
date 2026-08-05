from abc import ABC, abstractmethod

from pydantic import BaseModel


class Finding(BaseModel):
    title: str
    severity: str  # critical, high, medium, low, info
    description: str
    recommendation: str | None = None
    source: str | None = None


class BaseParser(ABC):
    @abstractmethod
    async def parse(self, content: bytes) -> dict:
        """Parse uploaded file content into structured data."""
        ...
