from typing import Optional
import chess
from deep_chess_playground.utils.square_utilities import Square, ALL_SQUARES
from typing import Dict


class Move:
    """A class representing a chess move."""
    def __init__(self, move_string: str):
        self._move_string = move_string
        self._source_square = ALL_SQUARES[move_string[0:2]]
        self._dest_square = ALL_SQUARES[move_string[2:4]]
        self._promotion = move_string[4] if len(move_string) > 4 else None
        self._file_diff = ord(self.dest_square.file) - ord(self.source_square.file)
        self._rank_diff = ord(self.dest_square.rank) - ord(self.source_square.rank)
        self._direction = self._chess_move_to_direction()
        self._square_distance = max(abs(self._file_diff), abs(self._rank_diff))
        self._knight_move = (True if self._square_distance == 2
                             and (self._file_diff == 1 or self._rank_diff == 1)
                             else False)

    @property
    def move_string(self) -> str:
        """The four characters string representing the move."""
        return self._move_string

    @property
    def source_square(self) -> Square:
        """The starting square of the move."""
        return self._source_square

    @property
    def dest_square(self) -> Square:
        """The ending square of the move."""
        return self._dest_square

    @property
    def promotion(self) -> Optional[str]:
        """The promotion type of the move."""
        return self._promotion

    @property
    def direction(self) -> int:
        """The direction of the move. They are 8 possible directions: N, NE, E, SE, S, SW, W, NW,
        which are represented as 0, 1, 2, 3, 4, 5, 6, 7."""
        return self._direction

    @property
    def square_distance(self) -> int:
        """The number of king steps from the starting square to the ending square."""
        return self._square_distance

    @property
    def knight_move(self) -> bool:
        """Whether the move is a knight move."""
        return self._knight_move

    def _chess_move_to_direction(self) -> int:
        """The direction of the move. They are 8 possible directions: N, NE, E, SE, S, SW, W, NW,
        which are represented as 0, 1, 2, 3, 4, 5, 6, 7."""
        if self._rank_diff > 0 and self._file_diff == 0:
            return 0  # N
        elif self._rank_diff > 0 and self._file_diff > 0:
            return 1  # NE
        elif self._rank_diff == 0 and self._file_diff > 0:
            return 2  # E
        elif self._rank_diff < 0 < self._file_diff:
            return 3  # SE
        elif self._rank_diff < 0 and self._file_diff == 0:
            return 4  # S
        elif self._rank_diff < 0 and self._file_diff < 0:
            return 5  # SW
        elif self._rank_diff == 0 and self._file_diff < 0:
            return 6  # W
        elif self._rank_diff > 0 > self._file_diff:
            return 7  # NW
        else:
            raise Exception("Invalid move")

    def __str__(self):
        return self.move_string

    def __repr__(self):
        return self.move_string

    def __eq__(self, other):
        return self.move_string == other.move_string

    def __ne__(self, other):
        return self.move_string != other.move_string


def generate_all_possible_moves() -> Dict[str, Move]:
    """Generates all possible legal moves in chess.
    A move is represented as a string in uci format e.g. e2e4. So there is starting and ending square.
    Move with promotion (e.g. a7a8q) is considered different from a7a8 (non pawn move from the 7th to 8th rank).
    There are 1968 possible moves (1792 no-promotion moves, 88 promotion moves for white and 88 for black)."""
    moves = {}
    board = chess.Board()
    # generate moves without promotion
    for square_name, square in ALL_SQUARES.items():
        board.clear_board()
        # queen moves
        board.set_piece_at((7-square.row)*8+square.col, chess.Piece.from_symbol('Q'))
        queen_moves = {str(mov): Move(move_string=str(mov)) for mov in list(board.legal_moves)}
        # knight moves
        board.set_piece_at((7-square.row)*8+square.col, chess.Piece.from_symbol('N'))
        knight_moves = {str(mov): Move(move_string=str(mov)) for mov in list(board.legal_moves)}
        moves.update({**queen_moves, **knight_moves})
    # generate moves with promotion
    promo_moves = {}
    for move_string, move in moves.items():
        if move.source_square.row == 6 and move.dest_square.row == 7 and move.square_distance == 1:
            for promo in ['q', 'r', 'b', 'n']:
                promo_move_string = move_string + promo
                promo_moves[promo_move_string] = Move(move_string=promo_move_string)
        elif move.source_square.row == 1 and move.dest_square.row == 0 and move.square_distance == 1:
            for promo in ['q', 'r', 'b', 'n']:
                promo_move_string = move_string + promo
                promo_moves[promo_move_string] = Move(move_string=promo_move_string)
    moves.update(promo_moves)
    return moves


ALL_POSSIBLE_MOVES = generate_all_possible_moves()
