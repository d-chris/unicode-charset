import hashlib
import json
import re
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Generator, Tuple
from urllib.request import urlopen


@contextmanager
def open(f: StringIO) -> Generator[StringIO, None, None]:
    pos = f.tell()

    try:
        f.seek(0)
        yield f
    finally:
        f.seek(pos)


class UnicodeBlocks(StringIO):

    url = "https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt"

    def __init__(self, blocks_txt: str = "", **kwargs) -> None:
        super().__init__(blocks_txt or self.fetch(), **kwargs)

        with open(self) as f:
            self._name = f.readline().strip("\n #")
            self._date = f.readline().split(":", maxsplit=1)[1].strip()

    @classmethod
    def fetch(cls) -> str:
        """Download latest 'blocks.txt' from unicode.org."""

        with urlopen(cls.url) as response:
            encoding = response.info().get_content_charset()
            return response.read().decode(encoding)

    @property
    def name(self) -> str:
        """Name of the Unicode Blocks file, extraced from the first line."""
        return self._name

    @property
    def date(self) -> str:
        """Date of the Unicode Blocks file, extraced from the second line."""
        return self._date

    def hexdigest(self, hash: str = "sha256", **kwargs) -> str:
        """Return the hexdigest of the Unicode Blocks file."""
        content = self.getvalue().encode()

        return hashlib.new(hash, content).hexdigest(**kwargs)

    def __iter__(self):
        regex = re.compile(
            r"^(?P<min>[0-9A-F]{3,6})\.\.(?P<max>[0-9A-F]{3,6})\;\s(?P<block>.*?)$",
            re.MULTILINE,
        )

        for match in regex.finditer(self.getvalue()):

            yield match.group("block"), (
                int(match.group("min"), 16),
                int(match.group("max"), 16),
            )

    def blocks(self) -> Dict[str, Tuple[int, int]]:
        """Return a dictionary of Unicode Blocks."""
        try:
            return self._blocks
        except AttributeError:
            self._blocks = dict(self)

        return self._blocks

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the Unicode Blocks file."""
        return {
            "name": self.name,
            "date": self.date,
            "url": self.url,
            "sha256": self.hexdigest(),
            "blocks": self.blocks(),
        }

    def save(self, json_file) -> Path:

        file = Path(json_file)

        file.write_text(json.dumps(self.to_dict(), separators=(",", ":")))

        return Path

    @staticmethod
    def load(json_file) -> Dict[str, Any]:

        return json.loads(Path(json_file).read_text("utf-8"))


def main():
    blocks = UnicodeBlocks()

    blocks.save(
        Path(__file__).parent.joinpath("blocks.json"),
    )


if __name__ == "__main__":
    main()
