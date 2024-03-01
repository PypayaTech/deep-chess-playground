import itertools
import re
import torch
from src.utils.position import Position
from src.utils.square_utilities import ALL_SQUARES

PIECE_CHANNEL_DICT = {
    'P': 0,
    'N': 1,
    'B': 2,
    'R': 3,
    'Q': 4,
    'K': 5,
    'p': 6,
    'n': 7,
    'b': 8,
    'r': 9,
    'q': 10,
    'k': 11
}


class PositionEncoder:
    """A class used to encode chess positions."""
    def encode_position(self, position: Position) -> torch.Tensor:
        """Concatenates all the planes (piece placement, who's turn, castling privileges etc.) in to one."""
        return torch.cat(tensors=(self.encode_piece_placement(position.piece_placement),
                                  self.encode_on_move(position.on_move),
                                  self.encode_castling_privileges(f'{position.white_kingside_castle}'
                                                                  f'{position.white_queenside_castle}'
                                                                  f'{position.black_kingside_castle}'
                                                                  f'{position.black_queenside_castle}'),
                                  self.encode_en_passant_index(position.en_passant_index),
                                  self.encode_half_moves(position.half_moves),
                                  self.encode_full_moves(position.full_moves),
                                  self.encode_controlled_squares(position.controlled_squares),
                                  self.encode_pins(position.pins)
                                  ),
                         dim=2)

    def decode_position(self, encoded_position: torch.Tensor) -> str:
        """Decodes an encoded position tensor into a FEN string.

        Args:
            encoded_position: A 8x8xn tensor encoding the FEN of a chess position.

        Returns:
            A string representing the FEN of the chess position.
        """
        piece_placement = self.decode_piece_placement(encoded_position[:, :, 0:12])
        on_move = self.decode_on_move(encoded_position[:, :, 12])
        castling_privileges = self.decode_castling_privileges(encoded_position[:, :, 13])
        en_passant_index = self.decode_en_passant_index(encoded_position[:, :, 14])
        half_moves = self.decode_half_moves(encoded_position[:, :, 15])
        full_moves = self.decode_full_moves(encoded_position[:, :, 16])
        return f"{piece_placement} {on_move} {castling_privileges} {en_passant_index} {half_moves} {full_moves}"

    @staticmethod
    def encode_piece_placement(piece_placement: str) -> torch.Tensor:
        """Encodes the piece placement into a 8x8x12 tensor.

            Args:
                piece_placement: A string representing the piece placement in FEN notation,
                    but you use periods instead of numbers to represent empty squares.

            Returns:
                An 8x8x12 tensor encoding the piece placement.
        """
        encoded_position = torch.zeros((8, 8, 12), dtype=torch.float32)
        for i in range(len(piece_placement)):
            if piece_placement[i] != '.':
                encoded_position[int(i / 8), int(i % 8), PIECE_CHANNEL_DICT[piece_placement[i]]] = 1
        return encoded_position

    @staticmethod
    def decode_piece_placement(encoded_piece_placement: torch.Tensor) -> str:
        """Decodes the encoded piece placement into a string in FEN notation.

        Args:
            encoded_piece_placement: An 8x8x12 tensor encoding the piece placement.

        Returns:
            A string representing the piece placement in FEN notation.
        """
        piece_placement = ""
        for row in range(8):
            for col in range(8):
                for piece in PIECE_CHANNEL_DICT:
                    if encoded_piece_placement[row, col, PIECE_CHANNEL_DICT[piece]] == 1:
                        piece_placement += piece
                        break
                    else:
                        piece_placement += "."
        piece_placement = re.sub(r"(.{8})", r"\1/", piece_placement, 0, re.DOTALL)[:-1]
        piece_placement = "".join(
            [str(len(list(g))) if c == "." else "".join(list(g)) for c, g in itertools.groupby(piece_placement)])
        return piece_placement

    @staticmethod
    def encode_on_move(on_move: str) -> torch.Tensor:
        """Encodes the side to move into a 8x8x1 tensor.

        Args:
            on_move: A character representing the side to move, where w represents white and b represents black.

        Returns:
            A 8x8x1 tensor encoding the side to move.
        """
        on_move = 1 if on_move == "w" else 0
        return torch.ones((8, 8, 1), dtype=torch.float32) * on_move

    @staticmethod
    def decode_on_move(encoded_on_move: torch.Tensor) -> str:
        """Decodes the side to move from a 8x8x1 tensor.

        Args:
            encoded_on_move: A 8x8x1 tensor encoding the side to move.

        Returns:
            A character representing the side to move, where w represents white and b represents black.
        """
        return "w" if encoded_on_move[0, 0, 0] == 1 else "b"

    @staticmethod
    def encode_castling_privileges(castling_privileges: str) -> torch.Tensor:
        """Encodes the castling privileges into a 8x8x1 tensor."""
        plane = torch.zeros((8, 8, 1), dtype=torch.float32)
        if 'K' in castling_privileges:
            plane[7, 4:8] = 1
        if 'Q' in castling_privileges:
            plane[7, 0:5] = 1
        if 'k' in castling_privileges:
            plane[0, 4:8] = 1
        if 'q' in castling_privileges:
            plane[0, 0:5] = 1
        return plane

    @staticmethod
    def decode_castling_privileges(encoded_castling_privileges: torch.Tensor) -> str:
        """Decodes the encoded castling privileges into a string."""
        castling_privileges = ""
        if encoded_castling_privileges[7, 4:8].sum() == 4:
            castling_privileges += "K"
        if encoded_castling_privileges[7, 0:5].sum() == 5:
            castling_privileges += "Q"
        if encoded_castling_privileges[0, 4:8].sum() == 4:
            castling_privileges += "k"
        if encoded_castling_privileges[0, 0:5].sum() == 5:
            castling_privileges += "q"
        castling_privileges = "-" if castling_privileges == "" else castling_privileges
        return castling_privileges

    @staticmethod
    def encode_en_passant_index(en_passant_square: str) -> torch.Tensor:
        """Encodes the en passant square into an 8x8x1 tensor.

        Args:
            en_passant_square: string representing the en passant square,
                which is "-" if no en passant square is available.

        Returns:
            An 8x8x1 tensor encoding the en passant square.
        """
        plane = torch.zeros((8, 8, 1), dtype=torch.float32)
        if en_passant_square != "-":
            en_passant_index = ALL_SQUARES[en_passant_square].row, ALL_SQUARES[en_passant_square].col
            plane[en_passant_index[0], en_passant_index[1], 0] = 1
        return plane

    @staticmethod
    def decode_en_passant_index(encoded_en_passant_index: torch.Tensor) -> str:
        """Decodes the en passant square from an 8x8x1 tensor.

        Args:
            encoded_en_passant_index: An 8x8x1 tensor encoding the en passant square.

        Returns:
            string representing the en passant square, which is "-" if no en passant square is available.
        """
        row_index, col_index = torch.where(encoded_en_passant_index == 1)
        if len(row_index) == 0:
            return "-"
        row_index, col_index = row_index.item(), col_index.item()
        return chr(ord('a') + col_index) + str(8 - row_index)

    @staticmethod
    def encode_half_moves(half_moves: int) -> torch.Tensor:
        """Encodes the number of half moves into a 8x8x1 tensor.

        Args:
            half_moves: An integer representing the number of half moves.

        Returns:
            A 8x8x1 tensor encoding the number of half moves.
        """
        return torch.ones((8, 8, 1), dtype=torch.float32) * half_moves

    @staticmethod
    def decode_half_moves(encoded_half_moves: torch.Tensor) -> int:
        """Decodes the number of half moves from a 8x8x1 tensor.

        Args:
            encoded_half_moves: A 8x8x1 tensor encoding the number of half moves.

        Returns:
            An integer representing the number of half moves.
        """
        return encoded_half_moves[0, 0, 0]

    @staticmethod
    def encode_full_moves(full_moves: int) -> torch.Tensor:
        """Encodes the number of full moves into a 8x8x1 tensor.

        Args:
            full_moves: An integer representing the number of full moves.

        Returns:
            A 8x8x1 tensor encoding the number of full moves.
        """
        return torch.ones((8, 8, 1), dtype=torch.float32) * full_moves

    @staticmethod
    def decode_full_moves(encoded_full_moves: torch.Tensor) -> int:
        """Decodes the number of full moves from a 8x8x1 tensor.

        Args:
            encoded_full_moves: A 8x8x1 tensor encoding the number of full moves.

        Returns:
            An integer representing the number of full moves.
        """
        return encoded_full_moves[0, 0, 0]
    
    @staticmethod
    def encode_controlled_squares(controlled_squares: list) -> torch.Tensor:
        """Encodes the controlled squares into a 8x8x12 tensor.

        Args:
            attacks (list): A list of 12 sets, where the first 6 sets contain the squares attacked by white and the
                last 6 sets contain the squares attacked by black.

        Returns:
            torch.Tensor: A 8x8x12 tensor encoding the controlled squares.
        """
        encoded_attacks = torch.zeros((8, 8, 12), dtype=torch.float32)
        for i in range(12):
            for j in controlled_squares[i]:
                encoded_attacks[int(j / 8), int(j % 8), i] = 1
        return encoded_attacks
    
    @staticmethod
    def decode_controlled_squares(encoded_controlled_squares: torch.Tensor) -> list:
        """Decodes the controlled squares from a 8x8x12 tensor.

        Args:
            encoded_attacks: A 8x8x12 tensor encoding the controlled squares.

        Returns:
            A list of 12 sets, where the first 6 sets contain the squares attacked by white and the
            last 6 sets contain the squares attacked by black.
        """
        attacks = [set() for _ in range(12)]
        for i in range(8):
            for j in range(8):
                for k in range(12):
                    if encoded_controlled_squares[i, j, k] == 1:
                        attacks[k].add(i * 8 + j)
        return attacks

    @staticmethod
    def encode_pins(pins: list) -> torch.Tensor:
        """Encodes the pins into a 8x8x2 tensor.
        
        Args:
            pins: A list of two sets, where the first set contains the squares pinned by white and the second set
                contains the squares pinned by black.
                
        Returns:
            A 8x8x2 tensor encoding the pins.
        """
        encoded_pins = torch.zeros((8, 8, 2), dtype=torch.float32)
        for i in range(2):
            for j in pins[i]:
                encoded_pins[int(j / 8), int(j % 8), i] = 1
        return encoded_pins
    
    @staticmethod
    def decode_pins(encoded_pins: torch.Tensor) -> list:
        """Decodes the pins from a 8x8x2 tensor.
        
        Args:
            encoded_pins: A 8x8x2 tensor encoding the pins.
            
        Returns:
            A list of two sets, where the first set contains the squares pinned by white and the second set
            contains the squares pinned by black.
        """
        pins = [set() for _ in range(2)]
        for i in range(8):
            for j in range(8):
                for k in range(2):
                    if encoded_pins[i, j, k] == 1:
                        pins[k].add(i * 8 + j)
        return pins
