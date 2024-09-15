import torch
from deep_chess_playground.utils.move_utilities import ALL_POSSIBLE_MOVES


class MoveEncoder8x8x73:
    """The class is used to encode moves.

    "A move in chess may be described in two parts: selecting the piece to move, and then...".
    Check this paper for more details https://arxiv.org/abs/1712.01815.
    """

    def __init__(self):
        self._encodings = self._get_move_encodings()

    def encode(self, move: str):
        return self._encodings[move]

    def _get_move_encodings(self) -> dict[str, torch.Tensor]:
        move_encodings = {}
        for move_string, move in ALL_POSSIBLE_MOVES.items():
            current_tensor = torch.zeros((8, 8, 73), dtype=torch.float32)
            plane_number = self._get_plane_number(move_string)
            current_tensor[move.source_square.row, move.source_square.col, plane_number] = 1
            move_encodings[move_string] = current_tensor
        return move_encodings

    def _get_plane_number(self, move):
        if move.promotion is not None and move.promotion != "q":
            if move.direction == 0:  # N
                return {
                    "r": 64,
                    "b": 67,
                    "n": 70
                }[move.promotion]
            elif move.direction == 1:  # NE
                return {
                    "r": 65,
                    "b": 68,
                    "n": 71
                }[move.promotion]
            else:  # NW
                return {
                    "r": 66,
                    "b": 69,
                    "n": 72
                }[move.promotion]
        elif move.knight_move:
            return 56 + move.direction
        else:
            return move.direction * 7 + move.square_distance - 1
