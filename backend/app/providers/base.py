from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    @abstractmethod
    async def explain(self, findings: list[dict]) -> str:
        """Generate AI explanation for a set of findings."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the AI provider is available."""
        ...
