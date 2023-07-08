import pytest
from src.cnn.two_d_cnn.common.data_processing import position_encoding
from src.utils.position import Position


@pytest.mark.parametrize('fen', [
    'r1bqkbnr/ppp1pppp/2n5/1B1p4/3P4/4P3/PPP2PPP/RNBQK1NR b KQkq - 2 3',
    'R7/6p1/P1R2pkp/8/r3P1K1/5P1P/6r1/8 w - - 0 45',
    'r1b1k1nr/ppp1qppp/2n5/1B1p4/1b1p4/1PN1PN2/PBP2PPP/R2QK2R w KQkq - 0 8'
])
def test_controlled_squares_encoding_decoding(fen):
    position = Position(fen)
    encoder = position_encoding.PositionEncoder()
    encoded = encoder.encode_controlled_squares(position.controlled_squares)
    decoded = encoder.decode_controlled_squares(encoded)
    assert position.controlled_squares == decoded


@pytest.mark.parametrize('fen', [
    'r1bqkbnr/ppp1pppp/2n5/1B1p4/3P4/4P3/PPP2PPP/RNBQK1NR b KQkq - 2 3',
    'R7/6p1/P1R2pkp/8/r3P1K1/5P1P/6r1/8 w - - 0 45',
    'r1b1k1nr/ppp1qppp/2n5/1B1p4/1b1p4/1PN1PN2/PBP2PPP/R2QK2R w KQkq - 0 8'
])
def test_pin_encoding_decoding(fen):
    position = Position(fen)
    encoder = position_encoding.PositionEncoder()
    encoded = encoder.encode_pins(position.pins)
    decoded = encoder.decode_pins(encoded)
    assert position.pins == decoded
