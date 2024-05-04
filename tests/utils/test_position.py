import pytest
from src.utils.position import Position


@pytest.fixture
def default_position():
    return Position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")


@pytest.fixture
def custom_position():
    return Position("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq e6 0 3")


def test_initialization(default_position):
    assert isinstance(default_position, Position)


def test_fen_property(default_position):
    assert default_position.fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_piece_placement_property(default_position):
    expected = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    assert default_position.piece_placement == expected


def test_on_move_property(default_position, custom_position):
    assert default_position.on_move == 1
    assert custom_position.on_move == 1


def test_castling_rights(default_position, custom_position):
    assert default_position.white_kingside_castle == 1
    assert default_position.white_queenside_castle == 1
    assert default_position.black_kingside_castle == 1
    assert default_position.black_queenside_castle == 1

    assert custom_position.white_kingside_castle == 1
    assert custom_position.white_queenside_castle == 1
    assert custom_position.black_kingside_castle == 1
    assert custom_position.black_queenside_castle == 1


def test_en_passant_index(default_position, custom_position):
    assert default_position.en_passant_index is None
    assert custom_position.en_passant_index == (2, 4)  # e6 square


def test_half_moves_property(default_position, custom_position):
    assert default_position.half_moves == 0
    assert custom_position.half_moves == 0


def test_full_moves_property(default_position, custom_position):
    assert default_position.full_moves == 1
    assert custom_position.full_moves == 3


def test_controlled_squares_property(default_position):
    controlled_squares = default_position.controlled_squares
    assert len(controlled_squares) == 12
    assert isinstance(controlled_squares[0], set)


def test_pins_property(default_position):
    pins = default_position.pins
    assert len(pins) == 2
    assert isinstance(pins[0], set)


def test_str_representation(default_position):
    assert str(default_position) == default_position.fen


def test_repr_representation(default_position):
    assert repr(default_position) == f"Position('{default_position.fen}')"


def test_equality(default_position):
    same_position = Position(default_position.fen)
    different_position = Position("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")

    assert default_position == same_position
    assert default_position != different_position
    assert default_position != "not a position object"


def test_create_attacks(default_position):
    controlled_squares, pins = default_position._create_attacks()
    assert len(controlled_squares) == 12
    assert len(pins) == 2
    assert all(isinstance(attack_set, set) for attack_set in controlled_squares)
    assert all(isinstance(pin_set, set) for pin_set in pins)
