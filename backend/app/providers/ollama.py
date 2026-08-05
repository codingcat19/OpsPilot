from app.providers.base import BaseAIProvider


class OllamaProvider(BaseAIProvider):
    async def explain(self, findings: list[dict]) -> str:
        # TODO: implement Ollama API integration
        raise NotImplementedError

    async def health_check(self) -> bool:
        # TODO: implement health check
        raise NotImplementedError
