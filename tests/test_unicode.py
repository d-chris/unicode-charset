from sys import maxsize, maxunicode

import pytest

from charset.unicode import _assert_args, all_unicodes, urandom, urange, ushuffel


@pytest.fixture(
    params=[
        (10, 0),
        (0, maxsize),
        (-10, 20),
    ],
    ids=lambda x: repr(x),
)
def bad_limits(request):
    return request.param


@pytest.mark.parametrize(
    "min,max",
    [
        (0, 10),
        (-10, 0),
        (0, 20),
        (maxunicode - 10, maxunicode),
    ],
)
def test_generators(min, max):

    _random = sorted(urandom(max, min))
    _range = list(urange(max, min))

    assert _random == _range


@pytest.mark.parametrize(
    "func",
    [
        urange,
        ushuffel,
        urandom,
    ],
)
@pytest.mark.benchmark(group="unicode", warmup=False, min_rounds=1)
def test_benchmark(benchmark, func):

    kwargs = {
        "min": 0,
        "max": maxunicode,
    }

    result = benchmark(lambda: list(func(**kwargs)))

    assert len(result) == maxunicode + 1


def test_assert_false(bad_limits):
    min, max = bad_limits
    with pytest.raises(ValueError):
        _ = _assert_args(min, max)


@pytest.mark.parametrize(
    "min,max",
    [
        (None, None),
        (0, maxunicode),
        (None, 10),
        (10, 20),
    ],
)
def test_assert_true(min, max):
    a, o = _assert_args(min, max)

    assert a < o


def test_unicode():

    kwargs = {
        "names": False,
        "min": 0,
        "max": 5,
    }

    _range = [i[0] for i in all_unicodes(random=False, **kwargs)]
    _random = [i[0] for i in all_unicodes(random=True, **kwargs)]

    assert all(isinstance(i, str) for i in _random)
    assert sorted(_random) == _range


def test_unicode_names():

    kwargs = {
        "names": True,
        "max": 255,
    }
    _range = [i[1] for i in all_unicodes(random=False, **kwargs)]
    _random = [i[1] for i in all_unicodes(random=True, **kwargs)]

    assert all(i != "" for i in _random)
    assert sorted(_random) == sorted(_range)


def test_unicode_raises(bad_limits):
    min, max = bad_limits

    with pytest.raises(ValueError):
        _ = list(all_unicodes(names=False, min=min, max=max))
