import hcl2

from app.parsers.base import BaseParser

_BLOCK_MARKER = "__is_block__"


class TerraformParser(BaseParser):
    """Parse Terraform HCL2 files into normalized resources and variables."""

    async def parse(self, content: bytes) -> dict:
        text = content.decode("utf-8", errors="replace")
        parsed = hcl2.loads(text)
        return {
            "file_type": "terraform",
            "resources": self._resources(parsed),
            "variables": self._variables(parsed),
        }

    @classmethod
    def _resources(cls, parsed: dict) -> list[dict]:
        resources: list[dict] = []
        for block in parsed.get("resource", []):
            for resource_type, instances in block.items():
                for instance_name, attrs in instances.items():
                    resources.append(
                        {
                            "type": cls._unquote(resource_type),
                            "name": cls._unquote(instance_name),
                            "attrs": cls._clean(attrs),
                        }
                    )
        return resources

    @classmethod
    def _variables(cls, parsed: dict) -> list[dict]:
        variables: list[dict] = []
        for block in parsed.get("variable", []):
            for name, attrs in block.items():
                variables.append({"name": cls._unquote(name), "attrs": cls._clean(attrs)})
        return variables

    @classmethod
    def _clean(cls, value: object) -> object:
        if isinstance(value, dict):
            return {
                cls._unquote(str(key)): cls._clean(item)
                for key, item in value.items()
                if key != _BLOCK_MARKER
            }
        if isinstance(value, list):
            return [cls._clean(item) for item in value]
        if isinstance(value, str):
            return cls._unquote(value)
        return value

    @staticmethod
    def _unquote(value: str) -> str:
        if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value
