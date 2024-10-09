import pytest
import torch
from deep_chess_playground.data_encoders.input_encoders.grid_encoding import GridEncoder
from deep_chess_playground.utils.square_utilities import ALL_SQUARES


class TestGridEncoder:
    @pytest.fixture
    def sample_fen(self):
        return "r3k2r/pp1p1pp1/3bq2p/1B6/3n2bP/P3PN2/1PQ1KPP1/R6R w - - 0 1"

    @pytest.fixture
    def expected_piece_placement(self):
        return {
            0: ["a3", "b2", "e3", "f2", "g2", "h4"],  # White pawns
            1: ["f3"],  # White knights
            2: ["b5"],  # White bishops
            3: ["a1", "h1"],  # White rooks
            4: ["c2"],  # White queen
            5: ["e2"],  # White king
            6: ["a7", "b7", "d7", "f7", "g7", "h6"],  # Black pawns
            7: ["d4"],  # Black knights
            8: ["d6", "g4"],  # Black bishops
            9: ["a8", "h8"],  # Black rooks
            10: ["e6"],  # Black queen
            11: ["e8"],  # Black king
        }

    @pytest.fixture
    def expected_controlled_squares(self):
        return {
            12: ["a3", "b4", "c3", "d4", "e3", "f3", "f4", "g3", "g5", "h3"],
            13: ["d2", "d4", "e1", "e5", "g1", "g5", "h2", "h4"],
            14: ["a4", "a6", "c4", "c6", "d3", "d7", "e2"],
            15: ["a1", "a2", "a3", "b1", "c1", "d1", "e1", "f1", "g1", "h1", "h2", "h3", "h4"],
            16: ["a4", "b1", "b2", "b3", "c1", "c3", "c4", "c5", "c6", "c7", "c8", "d1", "d2", "d3", "e2", "e4", "f5", "g6", "h7"],
            17: ["d1", "d2", "d3", "e1", "e3", "f1", "f2", "f3"],
            18: ["a6", "b6", "c6", "e6", "f6", "g5", "g6", "h6"],
            19: ["b3", "b5", "c2", "c6", "e2", "e6", "f3", "f5"],
            20: ["a3", "b4", "b8", "c5", "c7", "e5", "e6", "e7", "f3", "f4", "f5", "f8", "g3", "h2", "h3", "h5"],
            21: ["a7", "b8", "c8", "d8", "e8", "f8", "g8", "h6", "h7"],
            22: ["a2", "b3", "c4", "d5", "d6", "d7", "e3", "e4", "e5", "e7", "e8", "f5", "f6", "f7", "g4", "g6", "h6"],
            23: ["d7", "d8", "e7", "f7", "f8"]
        }

    def test_grid_encoder_piece_placement(self, sample_fen, expected_piece_placement):
        encoder = GridEncoder()
        output = encoder.encode(sample_fen)

        for channel, squares in expected_piece_placement.items():
            for square in squares:
                sq = ALL_SQUARES[square]
                assert output[
                           channel, sq.row, sq.col] == 1, f"Piece placement: Channel {channel}, square {square} should be 1"

            # Check that all other squares in this channel are 0
            for sq in ALL_SQUARES.values():
                if sq.square_name not in squares:
                    assert output[
                               channel, sq.row, sq.col] == 0, f"Piece placement: Channel {channel}, square {sq} should be 0"

        # Check that the sum of all piece placement channels equals the number of pieces
        assert torch.sum(output[:12]) == sum(
            len(squares) for squares in expected_piece_placement.values()), "Total number of pieces doesn't match"

    def test_grid_encoder_controlled_squares(self, sample_fen, expected_controlled_squares):
        encoder = GridEncoder()
        output = encoder.encode(sample_fen)

        for channel, squares in expected_controlled_squares.items():
            for square in squares:
                sq = ALL_SQUARES[square]
                assert output[
                           channel, sq.row, sq.col] == 1, f"Controlled squares: Channel {channel}, square {square} should be 1"

            # Check that all other squares in this channel are 0
            for sq in ALL_SQUARES.values():
                if sq.square_name not in squares:
                    assert output[
                               channel, sq.row, sq.col] == 0, f"Controlled squares: Channel {channel}, square {sq} should be 0"

    def test_grid_encoder_output_shape(self, sample_fen):
        encoder = GridEncoder()
        output = encoder.encode(sample_fen)
        assert output.shape == (24, 8, 8), "Output tensor should have shape (24, 8, 8)"

    def test_grid_encoder_dtype(self, sample_fen):
        encoder = GridEncoder()
        output = encoder.encode(sample_fen)
        assert output.dtype == torch.float32, "Output tensor should be of type float32"

    def test_grid_encoder_invalid_fen(self):
        encoder = GridEncoder()
        with pytest.raises(ValueError):
            encoder.encode("invalid fen string")

    def test_grid_encoder_empty_board(self):
        encoder = GridEncoder()
        empty_fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        output = encoder.encode(empty_fen)
        assert torch.sum(output) == 0, "Empty board should have all zeros in the output tensor"

    def test_grid_encoder_starting_position(self):
        encoder = GridEncoder()
        starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        output = encoder.encode(starting_fen)

        # Check piece placement channels
        assert torch.sum(output[0]) == 8, "Should have 8 white pawns"
        assert torch.sum(output[1]) == 2, "Should have 2 white knights"
        assert torch.sum(output[2]) == 2, "Should have 2 white bishops"
        assert torch.sum(output[3]) == 2, "Should have 2 white rooks"
        assert torch.sum(output[4]) == 1, "Should have 1 white queen"
        assert torch.sum(output[5]) == 1, "Should have 1 white king"
        assert torch.sum(output[6]) == 8, "Should have 8 black pawns"
        assert torch.sum(output[7]) == 2, "Should have 2 black knights"
        assert torch.sum(output[8]) == 2, "Should have 2 black bishops"
        assert torch.sum(output[9]) == 2, "Should have 2 black rooks"
        assert torch.sum(output[10]) == 1, "Should have 1 black queen"
        assert torch.sum(output[11]) == 1, "Should have 1 black king"

        # Basic check for control channels (not exhaustive)
        assert torch.sum(output[12:]) > 0, "Control channels should not be all zero"

    @pytest.mark.parametrize("fen, expected_sum", [
        ("8/8/8/8/8/8/8/8 w - - 0 1", 0),  # Empty board
        ("4k3/8/8/8/8/8/8/4K3 w - - 0 1", 2),  # Only kings
        ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 32)  # Starting position
    ])
    def test_grid_encoder_piece_count(self, fen, expected_sum):
        encoder = GridEncoder()
        output = encoder.encode(fen)
        piece_sum = torch.sum(output[:12])  # Sum of first 12 channels (piece placement)
        assert piece_sum == expected_sum, f"Total piece count for FEN {fen} should be {expected_sum}"
