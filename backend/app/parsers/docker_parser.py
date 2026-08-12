from app.parsers.base import BaseParser


class DockerParser(BaseParser):
    """Parse a Dockerfile into normalized instructions and base-image stages."""

    async def parse(self, content: bytes) -> dict:
        text = content.decode("utf-8", errors="replace")
        instructions = self._parse_instructions(text)
        stages = [
            stage
            for instruction in instructions
            if instruction["instruction"] == "FROM"
            if (stage := self._parse_from(instruction["value"])) is not None
        ]
        return {
            "file_type": "docker",
            "instructions": instructions,
            "stages": stages,
        }

    @staticmethod
    def _parse_instructions(text: str) -> list[dict]:
        """Split into logical lines (continuations joined), dropping blanks and # comments."""
        instructions: list[dict] = []
        buf: list[str] = []
        lines = text.splitlines()
        for lineno, raw in enumerate(lines, start=1):
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            if line.endswith("\\"):
                buf.append(line[:-1].rstrip())
                continue
            buf.append(line)
            instructions.append(DockerParser._to_instruction(" ".join(buf), lineno))
            buf = []
        if buf:
            instructions.append(DockerParser._to_instruction(" ".join(buf), len(lines)))
        return instructions

    @staticmethod
    def _to_instruction(logical_line: str, lineno: int) -> dict:
        instruction, _, value = logical_line.partition(" ")
        return {"instruction": instruction.upper(), "value": value, "line": lineno}

    @staticmethod
    def _parse_from(value: str) -> dict | None:
        parts = value.split()
        if not parts:
            return None
        alias = parts[2] if len(parts) >= 3 and parts[1].upper() == "AS" else None
        image, tag = DockerParser._split_image(parts[0])
        return {"image": image, "tag": tag, "alias": alias}

    @staticmethod
    def _split_image(image_part: str) -> tuple[str, str | None]:
        if "@" in image_part:
            repo, digest = image_part.split("@", 1)
            return repo, f"@{digest}"
        if ":" in image_part:
            repo, _, tag = image_part.rpartition(":")
            if "/" in tag:  # registry:port/image, not an image tag
                return image_part, None
            return repo, tag
        return image_part, None
