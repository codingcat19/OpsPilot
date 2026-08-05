from app.providers.base import BaseAIProvider


class GroqProvider(BaseAIProvider):
    async def explain(self, findings: list[dict]) -> str:
        # TODO: implement Groq API integration
        raise NotImplementedError

    async def health_check(self) -> bool:
        # TODO: implement health check
        raise NotImplementedError
