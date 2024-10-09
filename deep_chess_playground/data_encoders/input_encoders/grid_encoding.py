import torch
import chess


class GridEncoder:
    def __init__(self):
        self.piece_to_index = {
            'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
            'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
        }

    def encode(self, fen):
        board = chess.Board(fen)
        tensor = torch.zeros(24, 8, 8)

        # Encode piece positions
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                row, col = divmod(square, 8)
                tensor[self.piece_to_index[piece.symbol()]][7 - row][col] = 1

        # Encode controlled squares
        for piece_type in range(1, 7):  # 1=Pawn, 2=Knight, ..., 6=King
            for color in [chess.WHITE, chess.BLACK]:
                channel = self.piece_to_index[chess.Piece(piece_type, color).symbol()]
                for from_square in chess.SQUARES:
                    piece = board.piece_at(from_square)
                    if piece and piece.piece_type == piece_type and piece.color == color:
                        for to_square in board.attacks(from_square):
                            row, col = divmod(to_square, 8)
                            tensor[channel + 12][7 - row][col] = 1

        return tensor
