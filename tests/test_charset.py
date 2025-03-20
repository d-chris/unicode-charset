from collections.abc import Iterable

import pytest

from charset.charset import CharSet, all_charsets, charset


def test_namedtuple():
    space = ("utf-8", " ", "SPACE")

    char = CharSet(*space)

    assert isinstance(char.chr.encode(space[0]), bytes), "cannot be encoded"
    assert str(char) == space[1], "wrong string representation"
    assert char.name == space[2], "has wrong name"
    assert char.ord == ord(space[1]), "has wrong ordinal value"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n": -1, "encoding": "utf-8"},
        {"n": 1, "encoding": "fubar"},
    ],
    ids=lambda x: repr(x),
)
def test_charset_raises(kwargs):
    with pytest.raises(ValueError):
        list(charset(**kwargs))


def test_charset_iterable():

    gen = charset("utf-8", random=False)

    assert isinstance(gen, Iterable)
    assert isinstance(next(gen), CharSet)


def test_charset():

    n = 10

    chars = [c for c in charset("ansi", n=n, min=255, random=False)]

    assert len(chars) == n
    assert all(isinstance(c, CharSet) for c in chars)


def test_wrong_encoding():

    assert list(charset("base64")) == []


@pytest.mark.slow
def test_ansi_charset():

    ansi = charset("ansi", random=False, names=False)

    assert len(list(ansi)) == 256


def test_all_charsets():

    gen = all_charsets(n=1)

    assert isinstance(next(gen), CharSet)
