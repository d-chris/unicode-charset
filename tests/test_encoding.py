from collections.abc import Iterable

import pytest

from charset.encoding import (
    AllEncodings,
    ValidEncodings,
    all_encodings,
    valid_encodings,
)


@pytest.mark.parametrize(
    "var, obj",
    [
        (all_encodings, AllEncodings),
        (valid_encodings, ValidEncodings),
    ],
    ids=[
        "all_encodings",
        "valid_encodings",
    ],
)
def test_singelton(var, obj):

    assert id(var) == id(obj())


def test_contains_valid_encodings(venc):
    assert venc in valid_encodings


def test_call_valid_encodings(venc):
    assert valid_encodings(venc)


def test_iter_all_encodings():

    assert isinstance(all_encodings, Iterable)
    assert next(iter(all_encodings))


def test_contains_all_encodings(aenc):
    assert aenc in all_encodings


def test_call_all_encodings():
    assert isinstance(all_encodings(), set)
