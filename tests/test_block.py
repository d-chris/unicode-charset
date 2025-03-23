import pytest

from charset.__main__ import UnicodeBlocks

dataset = UnicodeBlocks.load("charset/blocks.txt")["blocks"]


@pytest.fixture(params=dataset.keys())
def name(request):
    return request.param


@pytest.fixture(params=[name for name in dataset.keys() if len(name.split()) > 4])
def words(request):
    return request.param


@pytest.mark.parametrize(
    "func",
    [
        str,
        str.upper,
        lambda x: str(x).replace(" ", "_").upper(),
        lambda x: str(x).replace(" ", "-").upper(),
    ],
    ids=[
        "str",
        "upper",
        "replace_underscore",
        "replace_dash",
    ],
)
def test_names(name, func):

    match = dataset[func(name)]

    assert name == match.name


@pytest.mark.parametrize("n", [1, 2])
def test_words(words, n):

    tokens = words.split()

    search = " ".join(tokens[:n] + tokens[n + 1 :])  # noqa: E203

    match = dataset[search]

    assert words == match.name
