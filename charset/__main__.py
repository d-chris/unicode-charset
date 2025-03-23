import hashlib
import re
from collections.abc import Generator
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any, Optional
from urllib.request import urlopen

from frozendict import frozendict


class BlockTuple(tuple):
    """tuple which behaves like a named tuple with a hidden attribute name."""

    def __new__(cls, min_val: int, max_val: int, name: str):
        obj = super().__new__(cls, (min_val, max_val))
        obj._name = name
        return obj

    @property
    def min(self) -> int:
        return self[0]

    @property
    def max(self) -> int:
        return self[1]

    @property
    def name(self) -> str:
        return self._name


@dataclass(frozen=True)
class UnicodeBlocks:
    name: str
    date: str
    url: str
    sha256: str
    blocks: frozendict[str, BlockTuple] = field(repr=False)


class UnicodeBlockFile(StringIO):

    url = "https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt"

    def __init__(self, blocks_txt: str = "", **kwargs) -> None:
        super().__init__(blocks_txt or self.fetch(), **kwargs)

        self._name = self.readline().strip("\n #")
        self._date = self.readline().split(":", maxsplit=1)[1].strip()

        self.seek(0)

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

    def __iter__(self) -> Generator[tuple[str, BlockTuple], None, None]:
        """Iterate over the Unicode Blocks file."""

        regex = re.compile(
            r"^(?P<min>[0-9A-F]{3,6})\.\.(?P<max>[0-9A-F]{3,6})\;\s(?P<block>.*?)$",
            re.MULTILINE,
        )

        for match in regex.finditer(self.getvalue()):
            name = match.group("block")
            min = int(match.group("min"), 16)
            max = int(match.group("max"), 16)

            yield name, BlockTuple(min, max, name)

    def blocks(self) -> frozendict[str, BlockTuple]:
        """Return a frozen dictionary of Unicode Blocks."""
        try:
            return self._blocks
        except AttributeError:
            self._blocks = frozendict(self)

        return self._blocks

    def export(self) -> UnicodeBlocks:
        """Return a dataclass to representation the Unicode Blocks file."""
        return UnicodeBlocks(
            name=self.name,
            date=self.date,
            url=self.url,
            sha256=self.hexdigest(),
            blocks=self.blocks(),
        )

    def save(self, filename: str) -> Path:
        """Save the Unicode Blocks file to plain text."""

        file = Path(filename)

        content = self.getvalue()

        file.write_text(content, encoding="utf-8")

        return file

    @classmethod
    def load(
        cls,
        block_file: Optional[str] = None,
        strict: bool = False,
    ) -> frozendict[str, Any]:
        """Load the Unicode Blocks file  text file or unicode.org URL."""

        try:
            block_file = Path(block_file).resolve(strict=True)
        except (FileNotFoundError, TypeError) as e:
            if strict:
                raise e

            instance = cls()
        else:
            instance = cls(block_file.read_text("utf-8"))

        return instance.export()
