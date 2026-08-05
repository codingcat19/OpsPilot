from app.parsers.base import BaseParser


class DockerParser(BaseParser):
    async def parse(self, content: bytes) -> dict:
        # TODO: implement Dockerfile parsing
        raise NotImplementedError
