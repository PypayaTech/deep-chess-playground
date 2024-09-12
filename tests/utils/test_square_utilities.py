import pytest as pytest
from deep_chess_playground.utils.square_utilities import Square, ALL_SQUARES


@pytest.mark.parametrize("square_name, expected_file,expected_rank,expected_row,expected_col,expected_index", [
    ("a1", "a", "1", 7, 0, 56),
    ("b2", "b", "2", 6, 1, 49),
    ("h8", "h", "8", 0, 7, 7)
])
def test_square_init(square_name, expected_file, expected_rank,
                     expected_row, expected_col, expected_index):
    square = Square(square_name)
    assert square.square_name == square_name
    assert square.file == expected_file
    assert square.rank == expected_rank
    assert square.row == expected_row
    assert square.col == expected_col
    assert square.index == expected_index


@pytest.mark.parametrize("square_name,expected_exc", [
    ("a0", ValueError),
    ("a9", ValueError),
    ("i1", ValueError),
    ("a", ValueError),
    ("1", ValueError)
])
def test_square_init_invalid(square_name, expected_exc):
    with pytest.raises(expected_exc):
        Square(square_name)


@pytest.mark.parametrize("square_name,expected_str,expected_repr", [
    ("a1", "a1", "a1"),
    ("b2", "b2", "b2"),
    ("h8", "h8", "h8"),
    ("d4", "d4", "d4"),
    ("e5", "e5", "e5")
])
def test_square_str_repr(square_name, expected_str, expected_repr):
    square = Square(square_name)
    assert str(square) == expected_str
    assert repr(square) == expected_repr


@pytest.mark.parametrize("square1,square2,expected_eq,expected_ne", [
    ("a1", "a1", True, False),
    ("b2", "b2", True, False),
    ("h8", "h8", True, False),
    ("d4", "d4", True, False),
    ("e5", "e5", True, False),
    ("a1", "a2", False, True),
    ("b2", "c2", False, True),
    ("h8", "a1", False, True),
    ("d4", "d5", False, True),
    ("e5", "e6", False, True)
])
def test_square_eq_ne(square1, square2, expected_eq, expected_ne):
    square1 = Square(square1)
    square2 = Square(square2)
    assert (square1 == square2) == expected_eq
    assert (square1 != square2) == expected_ne


def test_len_all_squares():
    assert len(ALL_SQUARES) == 64
