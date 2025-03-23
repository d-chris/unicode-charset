import hashlib
import re
from collections.abc import Generator
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from rapidfuzz import fuzz, process


@contextmanager
def open(f: StringIO) -> Generator[StringIO, None, None]:
    """Context manager to read always from the beginning of a StringIO object."""

    pos = f.tell()

    try:
        f.seek(0)
        yield f
    finally:
        f.seek(pos)


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


class BlocksDict(dict):

    _frozenerror = NotImplementedError("BlocksDict is frozen.")

    def __setitem__(self, key, value):
        raise self._frozenerror

    def __delitem__(self, key):
        raise self._frozenerror

    def update(self, *args, **kwargs):
        raise self._frozenerror

    def clear(self):
        raise self._frozenerror

    def pop(self, *args, **kwargs):
        raise self._frozenerror

    def popitem(self):
        raise self._frozenerror

    def setdefault(self, *args, **kwargs):
        raise self._frozenerror

    def __getitem__(self, key):
        try:
            data = super().__getitem__(key)
        except KeyError as e:
            # Try to find a close match
            matches = process.extractOne(
                str(key),
                self.keys(),
                score_cutoff=0.95,
                scorer=fuzz.QRatio,
                processor=str.capitalize,
            )  # difflib.get_close_matches(str(key), self, n=1, cutoff=0.5)

            if not matches:
                raise e

            data = super().__getitem__(matches[0])

        return data


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
            name = match.group("block")
            min = int(match.group("min"), 16)
            max = int(match.group("max"), 16)

            yield name, BlockTuple(min, max, name)

    def blocks(self) -> dict[str, tuple[int, int]]:
        """Return a dictionary of Unicode Blocks."""
        try:
            return self._blocks
        except AttributeError:
            self._blocks = BlocksDict(self)

        return self._blocks

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of the Unicode Blocks file."""
        return {
            "name": self.name,
            "date": self.date,
            "url": self.url,
            "sha256": self.hexdigest(),
            "blocks": self.blocks(),
        }

    def save(self, filename: str) -> Path:
        """Save the Unicode Blocks file as JSON or plain text."""

        file = Path(filename)

        content = self.getvalue()

        file.write_text(content, encoding="utf-8")

        return file

    @classmethod
    def load(cls, block_file, strict: bool = False) -> dict[str, Any]:
        """Load the Unicode Blocks file from JSON or plain text."""

        try:
            block_file = Path(block_file).resolve(strict=True)
        except FileNotFoundError as e:
            if strict:
                raise e

            data = cls()
        else:
            data = cls(block_file.read_text("utf-8"))

        return data.to_dict()
