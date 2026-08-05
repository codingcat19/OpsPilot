from app.parsers.base import BaseParser


class GitHubActionsParser(BaseParser):
    async def parse(self, content: bytes) -> dict:
        # TODO: implement GitHub Actions YAML parsing
        raise NotImplementedError
