from app.parsers.base import BaseParser


class TerraformParser(BaseParser):
    async def parse(self, content: bytes) -> dict:
        # TODO: implement Terraform file parsing
        raise NotImplementedError
