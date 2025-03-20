import pytest


@pytest.fixture(
    params=[
        "utf-8",
        "utf8",
        "utf_8",
        "latin-1",
        "latin1",
        "latin_1",
    ]
)
def venc(request):
    return request.param


@pytest.fixture(
    params=[
        "ascii",
        "utf_8",
        "cp1252",
    ]
)
def aenc(request):
    return request.param
