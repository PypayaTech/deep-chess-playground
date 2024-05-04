import json
import pytest
import torch
from src.data_encoders.input_encoders.grid_encoding import GridEncoder, GridDecoder
from src.utils.position import Position


@pytest.fixture
def default_config():
    return {
        "piece_placement": {"enabled": True},
        "on_move": {"enabled": True},
        "castling_rights": {"enabled": True},
        "en_passant": {"enabled": True},
        "half_moves": {"enabled": True},
        "full_moves": {"enabled": True},
        "controlled_squares": {"enabled": True},
        "pins": {"enabled": True}
    }


@pytest.fixture
def grid_encoder(default_config):
    return GridEncoder(default_config)


@pytest.fixture
def grid_decoder():
    return GridDecoder()


@pytest.mark.parametrize('fen', [
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'r1bqkbnr/ppp1pppp/2n5/1B1p4/3P4/4P3/PPP2PPP/RNBQK1NR b KQkq - 2 3',
    'R7/6p1/P1R2pkp/8/r3P1K1/5P1P/6r1/8 w - - 0 45',
    'r1b1k1nr/ppp1qppp/2n5/1B1p4/1b1p4/1PN1PN2/PBP2PPP/R2QK2R w KQkq - 0 8'
])
def test_encode_decode_position(grid_encoder, grid_decoder, fen):
    original_position = Position(fen)
    encoded = grid_encoder.encode_position(original_position)
    decoded_fen = grid_decoder.decode_position(encoded)

    # Create a new Position object from the decoded FEN
    decoded_position = Position(decoded_fen)

    # Compare the original and decoded positions
    assert decoded_position == original_position


def test_encode_piece_placement(grid_encoder):
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    position = Position(fen)
    encoded = grid_encoder._encode_piece_placement(position)
    assert encoded.shape == (8, 8, 12)
    assert encoded.sum() == 32  # Total number of pieces


def test_encode_decode_piece_placement(grid_encoder, grid_decoder):
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    position = Position(fen)
    encoded = grid_encoder._encode_piece_placement(position)
    decoded = grid_decoder._decode_piece_placement(encoded)
    assert decoded == 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'


@pytest.mark.parametrize('on_move', [1, 0])
def test_encode_on_move(grid_encoder, on_move):
    position = Position(f"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR {'w' if on_move else 'b'} KQkq - 0 1")
    encoded = grid_encoder._encode_on_move(position)
    assert encoded.shape == (8, 8, 1)
    assert torch.all(encoded == on_move)


def test_encode_castling_rights(grid_encoder):
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    position = Position(fen)
    encoded = grid_encoder._encode_castling_rights(position)
    assert encoded.shape == (8, 8, 1)
    assert encoded[7, 4:8, 0].sum() == 4  # White kingside
    assert encoded[7, 0:5, 0].sum() == 5  # White queenside
    assert encoded[0, 4:8, 0].sum() == 4  # Black kingside
    assert encoded[0, 0:5, 0].sum() == 5  # Black queenside


def test_encode_en_passant(grid_encoder):
    fen = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'
    position = Position(fen)
    encoded = grid_encoder._encode_en_passant(position)
    assert encoded.shape == (8, 8, 1)
    assert encoded[5, 4, 0] == 1  # e3 square


def test_encode_half_moves(grid_encoder):
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 10 1'
    position = Position(fen)
    encoded = grid_encoder._encode_half_moves(position)
    assert encoded.shape == (8, 8, 1)
    assert encoded[0, 0, 0] == 10


def test_encode_full_moves(grid_encoder):
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 15'
    position = Position(fen)
    encoded = grid_encoder._encode_full_moves(position)
    assert encoded.shape == (8, 8, 1)
    assert encoded[0, 0, 0] == 15


def test_encode_controlled_squares(grid_encoder):
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    position = Position(fen)
    encoded = grid_encoder._encode_controlled_squares(position)
    assert encoded.shape == (8, 8, 12)
    assert encoded.sum() > 0  # There should be some controlled squares


def test_encode_pins(grid_encoder):
    fen = 'rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2'
    position = Position(fen)
    encoded = grid_encoder._encode_pins(position)
    assert encoded.shape == (8, 8, 2)
    # No pins in this position
    assert encoded.sum() == 0


def test_from_json(tmp_path):
    config_path = tmp_path / "config.json"
    config = {
        'piece_placement': {'enabled': True},
        'on_move': {'enabled': False},
    }
    with open(config_path, 'w') as f:
        json.dump(config, f)

    encoder = GridEncoder.from_json(str(config_path))
    assert encoder.config == config


def test_from_dict():
    config = {
        'piece_placement': {'enabled': True},
        'on_move': {'enabled': False},
    }
    encoder = GridEncoder.from_dict(config)
    assert encoder.config == config
