import chess


class Position:
    def __init__(self, fen):
        self._fen = fen
        fen_elements = self._fen.split(' ')
        flatten_board = str(chess.Board(self._fen))
        self._piece_placement = flatten_board.replace(' ', '').replace('\n', '')
        self._on_move = 1 if fen_elements[1] == 'w' else 0
        self._white_kingside_castle = 1 if "K" in fen_elements[2] else 0
        self._white_queenside_castle = 1 if "Q" in fen_elements[2] else 0
        self._black_kingside_castle = 1 if "k" in fen_elements[2] else 0
        self._black_queenside_castle = 1 if "q" in fen_elements[2] else 0
        self._en_passant_index = (8 - int(fen_elements[3][1]), ord(fen_elements[3][0]) - ord('a')) \
            if fen_elements[3] != '-' else None
        self._half_moves = int(fen_elements[4])
        self._full_moves = int(fen_elements[5])
        self._baseBoard = chess.BaseBoard(fen_elements[0])
        self._controlled_squares, self._pins = self.create_attacks()
        
    @property
    def fen(self):
        return self._fen

    @property
    def piece_placement(self):
        return self._piece_placement

    @property
    def on_move(self):
        return self._on_move

    @property
    def white_kingside_castle(self):
        return self._white_kingside_castle

    @property
    def white_queenside_castle(self):
        return self._white_queenside_castle

    @property
    def black_kingside_castle(self):
        return self._black_kingside_castle

    @property
    def black_queenside_castle(self):
        return self._black_queenside_castle

    @property
    def en_passant_index(self):
        return self._en_passant_index

    @property
    def half_moves(self):
        return self._half_moves

    @property
    def full_moves(self):
        return self._full_moves
    
    @property
    def controlled_squares(self):
        return self._controlled_squares
    
    @property
    def pins(self):
        return self._pins

    def __str__(self):
        return self.fen

    def __repr__(self):
        return self.fen

    def __eq__(self, other):
        return self.fen == other.fen

    def __ne__(self, other):
        return self.fen != other.fen
    
    def create_attacks(self)->tuple:
        attacks = [set() for _ in range(12)]
        pins = [set(), set()]
        for square in range(64):
            i = self._baseBoard.piece_at(square)
            piece = i.piece_type - 1 + 6 * (not i.color)
            if i is not None:
                attacks[piece].update(self._baseBoard.attacks(square))
                temp_pins = list(self._baseBoard.pin(i.color, square))
                if len(temp_pins) != 64:
                    pins[not i.color].update(temp_pins)
        return attacks, pins
    
        
