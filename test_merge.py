"""Tests merge.py"""

import pytest
from merge import merge

# flake8: noqa
# pylint: disable=invalid-name,missing-function-docstring


@pytest.mark.parametrize("template, text, expected",
                         [[["### ###\n"], ["abc def\n"], ["abc def\n"]],
                          [["  # # #   \n"], ["  a b c\n"], ["  a b c   \n"]]
                          ])
def test_merge_page_good(template, text, expected):
    status, report = merge(template, text)
    assert report == expected
    assert status


@pytest.mark.parametrize("template, text",
                         [[["### ###\n"], ["abc\n"]],
                          [["  # # #   \n"], ["  a b cdef\n"]]
                          ])
def test_merge_page_bad(template, text):
    status, _ = merge(template, text)
    assert not status


@pytest.mark.parametrize("template, text",
                         [[["#\n", "#\n"], ["1\n"]],
                          [["#\n"], ["1\n", "2\n"]]
                          ])
def test_merge_page_length_mismatch(template, text):
    status, _ = merge(template, text)
    assert not status


def test_merge_page_shifted():
    template = ["                      ##     ###       #### ###\n",
                "  ### ######## ## ##        ####   ##  #### ###\n",
                "                      ##   #####       #### ###\n",
                "  #### ### ####               ###      #### ###\n"]
    text     = ["  AND CONTINUE AT 96  97      E51      U126 015\n",
                "                      96    30H0   96  U126 016\n",
                "  FIND ITS DSCN            10X20       U126 019\n",
                "                             J10       U126 020\n"]
    expected = "                      97     E51       U126 015\n" +\
               "  AND CONTINUE AT 96        30H0   96  U126 016\n" +\
               "                      96   10X20       U126 019\n" +\
               "  FIND ITS DSCN               J10      U126 020\n"

    status, report = merge(template, text)
    result = ''.join(report)
    assert result == expected
    assert status
