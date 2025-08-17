"""Test columns.py"""

import pytest
from columns import is_pole_whitespace, find_columns, get_column, paste_columns

# flake8: noqa
# pylint: disable=invalid-name,missing-function-docstring

grid1 = [
    "\n",
    " a aa  bb  \n",
    "           \n",
    "  aa   b   \n",
    "  a     b  \n",
    "   \n",
    ]


@pytest.mark.parametrize("pole, is_whitespace",
                         [[0, True],
                          [1, False],
                          [4, False],
                          [5, True],
                          [6, True],
                          [7, False],
                          ])
def test_is_pole_whitespace(pole, is_whitespace):
    assert is_pole_whitespace(grid1, pole) == is_whitespace

def test_find_columns():
    extents = find_columns(grid1)
    assert extents == [[0, 5], [5, 11]]
    col0 = get_column(grid1, extents[0])
    assert col0 == ["     ",
                    " a aa",
                    "     ",
                    "  aa ",
                    "  a  ",
                    "     "]
    col1 = get_column(grid1, extents[1])
    assert col1 == ["      ",
                    "  bb  ",
                    "      ",
                    "  b   ",
                    "   b  ",
                    "      "]

# grid1 contains short lines, which we expand into equal sized columns
# So use a version with complete lines only so we can compare the
# pasted with the original
grid_no_short = [
    "           \n",
    " a aa  bb  \n",
    "           \n",
    "  aa   b   \n",
    "  a     b  \n",
    "           \n",
    ]

def test_paste_columns():
    extents = find_columns(grid_no_short)
    cols = []
    for extent in extents:
        cols.append(get_column(grid_no_short, extent))
    pasted = paste_columns(cols)
    assert grid_no_short == pasted
