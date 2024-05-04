import torch
from typing import List, Dict, Any
import json
from src.utils.position import Position


class GridBase:
    """Base class for grid encoding and decoding."""

    @staticmethod
    def _square_to_algebraic(row: int, col: int) -> str:
        """Convert square coordinates to algebraic notation."""
        return f"{chr(ord('a') + col)}{8 - row}"

    @staticmethod
    def _algebraic_to_square(algebraic: str) -> tuple:
        """Convert algebraic notation to square coordinates."""
        return 8 - int(algebraic[1]), ord(algebraic[0]) - ord('a')


class GridEncoder(GridBase):
    """A class used to encode chess positions into grid representations."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the GridEncoder with a configuration.

        Args:
            config: A dictionary specifying which features to encode and how.
        """
        self.config = config

    @classmethod
    def from_json(cls, json_path: str) -> 'GridEncoder':
        """Create a GridEncoder instance from a JSON configuration file.

        Args:
            json_path: Path to the JSON configuration file.

        Returns:
            A GridEncoder instance.
        """
        with open(json_path, 'r') as f:
            config = json.load(f)
        return cls(config)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'GridEncoder':
        """Create a GridEncoder instance from a configuration dictionary.

        Args:
            config: A dictionary specifying which features to encode and how.

        Returns:
            A GridEncoder instance.
        """
        return cls(config)

    def encode_position(self, position: Position) -> torch.Tensor:
        """Encode a chess position into a grid representation.

        Args:
            position: A Position object representing the chess position.

        Returns:
            A tensor representing the encoded position.
        """
        encoded_features = []
        for feature, encoding_config in self.config.items():
            if encoding_config.get("enabled", True):
                method = getattr(self, f"_encode_{feature}")
                encoded_features.append(method(position, **encoding_config))
        return torch.cat(encoded_features, dim=2)

    def _encode_piece_placement(self, position: Position, **kwargs) -> torch.Tensor:
        """Encode the piece placement."""
        encoded = torch.zeros((8, 8, 12), dtype=torch.float32)
        piece_placement = position.piece_placement
        for i, piece in enumerate(piece_placement):
            if piece != '.':
                row, col = divmod(i, 8)
                piece_index = "PNBRQKpnbrqk".index(piece)
                encoded[row, col, piece_index] = 1
        return encoded

    def _encode_on_move(self, position: Position, **kwargs) -> torch.Tensor:
        """Encode who's turn it is to move."""
        return torch.full((8, 8, 1), float(position.on_move), dtype=torch.float32)

    def _encode_castling_privileges(self, position: Position, **kwargs) -> torch.Tensor:
        """Encode the castling rights."""
        encoded = torch.zeros((8, 8, 1), dtype=torch.float32)
        if position.white_kingside_castle:
            encoded[7, 4:8, 0] = 1
        if position.white_queenside_castle:
            encoded[7, 0:5, 0] = 1
        if position.black_kingside_castle:
            encoded[0, 4:8, 0] = 1
        if position.black_queenside_castle:
            encoded[0, 0:5, 0] = 1
        return encoded

    def _encode_en_passant(self, position: Position, **kwargs) -> torch.Tensor:
        """Encode the en passant square."""
        encoded = torch.zeros((8, 8, 1), dtype=torch.float32)
        if position.en_passant_index:
            row, col = position.en_passant_index
            encoded[row, col, 0] = 1
        return encoded

    def _encode_half_moves(self, position: Position, **kwargs) -> torch.Tensor:
        """Encode the number of half moves."""
        return torch.full((8, 8, 1), float(position.half_moves), dtype=torch.float32)

    def _encode_full_moves(self, position: Position, **kwargs) -> torch.Tensor:
        """Encode the number of full moves."""
        return torch.full((8, 8, 1), float(position.full_moves), dtype=torch.float32)

    def _encode_controlled_squares(self, position: Position, **kwargs) -> torch.Tensor:
        """Encode the controlled squares."""
        encoded = torch.zeros((8, 8, 12), dtype=torch.float32)
        for i, piece_control in enumerate(position.controlled_squares):
            for square in piece_control:
                row, col = divmod(square, 8)
                encoded[row, col, i] = 1
        return encoded

    def _encode_pins(self, position: Position, **kwargs) -> torch.Tensor:
        """Encode the pinned pieces."""
        encoded = torch.zeros((8, 8, 2), dtype=torch.float32)
        for i, side_pins in enumerate(position.pins):
            for square in side_pins:
                row, col = divmod(square, 8)
                encoded[row, col, i] = 1
        return encoded


class GridDecoder(GridBase):
    """A class used to decode grid representations into chess positions."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def decode_position(self, encoded_position: torch.Tensor) -> str:
        """Decode an encoded position tensor into a FEN string.

        Args:
            encoded_position: A 8x8xn tensor encoding the FEN of a chess position.

        Returns:
            A string representing the FEN of the chess position.
        """
        fen_parts = []
        current_index = 0

        for feature, encoding_config in self.config.items():
            if encoding_config.get("enabled", True):  # Default to True if "enabled" key is not present
                method = getattr(self, f"_decode_{feature}")
                feature_size = encoding_config.get("size", 1)
                fen_part = method(encoded_position[:, :, current_index:current_index + feature_size])
                fen_parts.append(fen_part)
                current_index += feature_size

        return " ".join(fen_parts)

    def _decode_piece_placement(self, encoded_piece_placement: torch.Tensor) -> str:
        """Decode the encoded piece placement into FEN notation."""
        pieces = "PNBRQKpnbrqk"
        fen_rows = []
        for row in range(8):
            fen_row = ''
            empty_count = 0
            for col in range(8):
                piece_index = encoded_piece_placement[row, col].argmax().item()
                if encoded_piece_placement[row, col, piece_index] > 0:  # A piece is present
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += pieces[piece_index]
                else:
                    empty_count += 1
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)

        return '/'.join(fen_rows)

    def _decode_on_move(self, encoded_on_move: torch.Tensor) -> str:
        """Decode the encoded on_move information."""
        return 'w' if encoded_on_move[0, 0, 0] > 0.5 else 'b'

    def _decode_castling_privileges(self, encoded_castling: torch.Tensor) -> str:
        """Decode the encoded castling privileges."""
        castling = ''
        if encoded_castling[7, 4:8, 0].sum() == 4:
            castling += 'K'
        if encoded_castling[7, 0:5, 0].sum() == 5:
            castling += 'Q'
        if encoded_castling[0, 4:8, 0].sum() == 4:
            castling += 'k'
        if encoded_castling[0, 0:5, 0].sum() == 5:
            castling += 'q'
        return castling if castling else '-'

    def _decode_en_passant(self, encoded_en_passant: torch.Tensor) -> str:
        """Decode the encoded en passant square."""
        non_zero = encoded_en_passant.nonzero()
        if len(non_zero) == 0:
            return '-'
        row, col = non_zero[0][:2]
        return self._square_to_algebraic(row, col)

    def _decode_half_moves(self, encoded_half_moves: torch.Tensor) -> str:
        """Decode the encoded half moves."""
        return str(int(encoded_half_moves[0, 0, 0].item()))

    def _decode_full_moves(self, encoded_full_moves: torch.Tensor) -> str:
        """Decode the encoded full moves."""
        return str(int(encoded_full_moves[0, 0, 0].item()))
