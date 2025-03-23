from pathlib import Path

import pytest
from frozendict import frozendict

from charset.block import BlockTuple, UnicodeBlockFile, UnicodeBlocks


@pytest.fixture
def blocktuple():
    return BlockTuple(0, 127, "Basic Latin")


@pytest.fixture(scope="session")
def unicodeblockfile():
    content = Path("charset/blocks.txt").read_text("utf-8")
    return UnicodeBlockFile(content)


def test_blocktuple_len(blocktuple):

    assert len(blocktuple) == 2


def test_blocktuple_unpack(blocktuple):

    min, max = blocktuple

    assert min == blocktuple.min
    assert max == blocktuple.max
    assert isinstance(blocktuple.name, str)


@pytest.mark.parametrize("attr", ["min", "max", "name"])
def test_blocktuple_name(blocktuple, attr):

    assert hasattr(blocktuple, attr)


def test_unicodeblocks_url():

    assert (
        UnicodeBlockFile.url
        == "https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt"
    )


@pytest.mark.parametrize("attr", ["name", "date"])
def test_unicodeblockfile_property(unicodeblockfile, attr):

    assert hasattr(unicodeblockfile, attr)
    assert isinstance(getattr(unicodeblockfile, attr), str)


def test_unicodeblockfile_hexdigest(unicodeblockfile):

    assert hasattr(unicodeblockfile, "hexdigest")
    assert isinstance(unicodeblockfile.hexdigest(), str)


def test_unicodeblockfiles_iter(unicodeblockfile):

    _name, _tuple = next(iter(unicodeblockfile))

    assert isinstance(_name, str)
    assert isinstance(_tuple, BlockTuple)


def test_unicodeblocks_block(unicodeblockfile):

    assert isinstance(unicodeblockfile.blocks(), frozendict)


def test_unicodeblocks_export(unicodeblockfile):

    assert isinstance(unicodeblockfile.export(), UnicodeBlocks)


def test_unicodeblocks_save(unicodeblockfile, tmp_path):

    file = Path(tmp_path).joinpath("Blocks.txt")

    unicodeblockfile.save(str(file))

    assert file.read_text("utf-8") == unicodeblockfile.getvalue()


def test_unicodeblocks_load():
    file = "charset/blocks.txt"

    ucd = UnicodeBlockFile.load(file)

    assert isinstance(ucd, UnicodeBlocks)


@pytest.mark.parametrize(
    "error, file",
    [
        (FileNotFoundError, "nofile.txt"),
        (TypeError, None),
    ],
)
def test_unicodeblocks_load_strict(error, file):

    with pytest.raises(error):
        UnicodeBlockFile.load(file, strict=True)


@pytest.mark.slow
def test_unicodeblocks_load_fetch():

    ucd = UnicodeBlockFile.load()

    assert isinstance(ucd, UnicodeBlocks)
