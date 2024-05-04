import chess
from typing import Optional, Tuple, List, Set


class Position:
    """A class representing a chess position.

    This class stores the chess position and provides methods to access various
    attributes of the position.

    Attributes:
        _fen (str): The Forsyth-Edwards Notation (FEN) string of the position.
        _piece_placement (str): A flattened string representation of the piece placement.
        _on_move (int): 1 if white to move, 0 if black to move.
        _white_kingside_castle (int): 1 if white can castle kingside, 0 otherwise.
        _white_queenside_castle (int): 1 if white can castle queenside, 0 otherwise.
        _black_kingside_castle (int): 1 if black can castle kingside, 0 otherwise.
        _black_queenside_castle (int): 1 if black can castle queenside, 0 otherwise.
        _en_passant_index (Optional[Tuple[int, int]]): The (row, col) of the en passant square, or None.
        _half_moves (int): The number of half moves since the last capture or pawn advance.
        _full_moves (int): The number of full moves in the game.
        _controlled_squares (List[Set[int]]): A list of sets representing controlled squares for each piece type.
        _pins (List[Set[int]]): A list of sets representing pinned pieces for each side.
    """

    def __init__(self, fen: str):
        self._fen = fen
        fen_elements = self._fen.split(' ')
        flatten_board = str(chess.Board(self._fen))
        self._piece_placement = flatten_board.replace(' ', '').replace('\n', '')
        self._on_move = 1 if fen_elements[1] == "w" else 0
        self._white_kingside_castle = 1 if "K" in fen_elements[2] else 0
        self._white_queenside_castle = 1 if "Q" in fen_elements[2] else 0
        self._black_kingside_castle = 1 if "k" in fen_elements[2] else 0
        self._black_queenside_castle = 1 if "q" in fen_elements[2] else 0
        self._en_passant_index = (8 - int(fen_elements[3][1]), ord(fen_elements[3][0]) - ord('a')) \
            if fen_elements[3] != '-' else None
        self._half_moves = int(fen_elements[4])
        self._full_moves = int(fen_elements[5])
        self._baseBoard = chess.BaseBoard(fen_elements[0])
        self._controlled_squares, self._pins = self._create_attacks()

    @property
    def fen(self) -> str:
        """Get the FEN string of the position."""
        return self._fen

    @property
    def piece_placement(self) -> str:
        """Get the flattened string representation of the piece placement."""
        return self._piece_placement

    @property
    def on_move(self) -> int:
        """Get who's turn it is to move (1 for white, 0 for black)."""
        return self._on_move

    @property
    def white_kingside_castle(self) -> int:
        """Get whether white can castle kingside (1) or not (0)."""
        return self._white_kingside_castle

    @property
    def white_queenside_castle(self) -> int:
        """Get whether white can castle queenside (1) or not (0)."""
        return self._white_queenside_castle

    @property
    def black_kingside_castle(self) -> int:
        """Get whether black can castle kingside (1) or not (0)."""
        return self._black_kingside_castle

    @property
    def black_queenside_castle(self) -> int:
        """Get whether black can castle queenside (1) or not (0)."""
        return self._black_queenside_castle

    @property
    def en_passant_index(self) -> Optional[Tuple[int, int]]:
        """Get the en passant square as (row, col), or None if not available."""
        return self._en_passant_index

    @property
    def half_moves(self) -> int:
        """Get the number of half moves since the last capture or pawn advance."""
        return self._half_moves

    @property
    def full_moves(self) -> int:
        """Get the number of full moves in the game."""
        return self._full_moves

    @property
    def controlled_squares(self) -> List[Set[int]]:
        """Get the list of sets representing controlled squares for each piece type."""
        return self._controlled_squares

    @property
    def pins(self) -> List[Set[int]]:
        """Get the list of sets representing pinned pieces for each side."""
        return self._pins

    def _create_attacks(self) -> Tuple[List[Set[int]], List[Set[int]]]:
        """Create lists of controlled squares and pins.

        Returns:
            A tuple containing two lists:
                - controlled_squares: A list of 12 sets representing squares controlled by each piece type.
                - pins: A list of 2 sets representing squares with pinned pieces for each side.
        """
        attacks = [set() for _ in range(12)]
        pins = [set() for _ in range(2)]
        for square in range(64):
            piece = self._baseBoard.piece_at(square)
            if piece is not None:
                piece_index = piece.piece_type - 1 + 6 * (not piece.color)
                attacks[piece_index].update(self._baseBoard.attacks(square))
                temp_pins = list(self._baseBoard.pin(piece.color, square))
                if len(temp_pins) != 64:
                    pins[not piece.color].update(temp_pins)
        return attacks, pins

    def __str__(self) -> str:
        return self.fen

    def __repr__(self) -> str:
        return f"Position('{self.fen}')"

    def __eq__(self, other: 'Position') -> bool:
        return isinstance(other, Position) and self.fen == other.fen

    def __ne__(self, other: 'Position') -> bool:
        return not self.__eq__(other)
