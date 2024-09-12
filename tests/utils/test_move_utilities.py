import pytest
from deep_chess_playground.utils.move_utilities import Move, ALL_POSSIBLE_MOVES
from deep_chess_playground.utils.square_utilities import Square


@pytest.mark.parametrize(
    "move_string,expected_source_square,expected_dest_square,expected_promotion,"
    "expected_direction,expected_square_distance,expected_knight_move", [
        ("e2e4", Square("e2"), Square("e4"), None, 0, 2, False),
        ("b1c3", Square("b1"), Square("c3"), None, 1, 2, True),
        ("h7h8q", Square("h7"), Square("h8"), "q", 0, 1, False),
        ("a7a8r", Square("a7"), Square("a8"), "r", 0, 1, False)
    ])
def test_move_init(move_string,
                   expected_source_square,
                   expected_dest_square,
                   expected_promotion,
                   expected_direction,
                   expected_square_distance,
                   expected_knight_move):
    move = Move(move_string)
    assert move.move_string == move_string
    assert move.source_square == expected_source_square
    assert move.dest_square == expected_dest_square
    assert move.promotion == expected_promotion
    assert move.direction == expected_direction
    assert move.square_distance == expected_square_distance
    assert move.knight_move == expected_knight_move


def test_no_promotion_moves_number():
    """Test that there are 1792 no promotion moves."""
    no_promotion_moves = [move for move in ALL_POSSIBLE_MOVES.values() if move.promotion is None]
    assert len(no_promotion_moves) == 1792


def test_white_promotion_moves_number():
    """Test that there are 88 promotion moves for white pieces."""
    white_promotion_moves = [move for move in ALL_POSSIBLE_MOVES.values()
                             if move.promotion is not None and move.source_square.rank == "7"]
    assert len(white_promotion_moves) == 88


def test_black_promotion_moves_number():
    """Test that there are 88 promotion moves for black pieces."""
    black_promotion_moves = [move for move in ALL_POSSIBLE_MOVES.values()
                             if move.promotion is not None and move.source_square.rank == "2"]
    assert len(black_promotion_moves) == 88
