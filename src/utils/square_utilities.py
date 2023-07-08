

class Square:
    def __init__(self, square_name: str):
        """A class representing the square on the chessboard."""
        if len(square_name) != 2:
            raise ValueError("Invalid square name (length should be 2).")
        if not square_name[0].isalpha() or not square_name[1].isdigit():
            raise ValueError("Invalid square name (first element must be a letter and second must be a digit).")
        if not 'a' <= square_name[0] <= 'h' or not '1' <= square_name[1] <= '8':
            raise ValueError("Invalid square name (file must be from a and h and rank must be from 1 and 8).")
        self._square_name = square_name
        self._file = square_name[0]
        self._rank = square_name[1]
        self._row = 7 - (int(square_name[1]) - 1)
        self._col = ord(square_name[0]) - ord('a')
        self._index = self._row * 8 + self._col

    @property
    def square_name(self):
        return self._square_name

    @property
    def file(self):
        return self._file

    @property
    def rank(self):
        return self._rank

    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self._col

    @property
    def index(self):
        return self._index

    def __str__(self):
        return self.square_name

    def __repr__(self):
        return self.square_name

    def __eq__(self, other):
        return self.square_name == other.square_name

    def __ne__(self, other):
        return self.square_name != other.square_name


ALL_SQUARES = {"a1": Square("a1"), "a2": Square("a2"), "a3": Square("a3"), "a4": Square("a4"), "a5": Square("a5"),
               "a6": Square("a6"), "a7": Square("a7"), "a8": Square("a8"),
               "b1": Square("b1"), "b2": Square("b2"), "b3": Square("b3"), "b4": Square("b4"), "b5": Square("b5"),
               "b6": Square("b6"), "b7": Square("b7"), "b8": Square("b8"),
               "c1": Square("c1"), "c2": Square("c2"), "c3": Square("c3"), "c4": Square("c4"), "c5": Square("c5"),
               "c6": Square("c6"), "c7": Square("c7"), "c8": Square("c8"),
               "d1": Square("d1"), "d2": Square("d2"), "d3": Square("d3"), "d4": Square("d4"), "d5": Square("d5"),
               "d6": Square("d6"), "d7": Square("d7"), "d8": Square("d8"),
               "e1": Square("e1"), "e2": Square("e2"), "e3": Square("e3"), "e4": Square("e4"), "e5": Square("e5"),
               "e6": Square("e6"), "e7": Square("e7"), "e8": Square("e8"),
               "f1": Square("f1"), "f2": Square("f2"), "f3": Square("f3"), "f4": Square("f4"), "f5": Square("f5"),
               "f6": Square("f6"), "f7": Square("f7"), "f8": Square("f8"),
               "g1": Square("g1"), "g2": Square("g2"), "g3": Square("g3"), "g4": Square("g4"), "g5": Square("g5"),
               "g6": Square("g6"), "g7": Square("g7"), "g8": Square("g8"),
               "h1": Square("h1"), "h2": Square("h2"), "h3": Square("h3"), "h4": Square("h4"), "h5": Square("h5"),
               "h6": Square("h6"), "h7": Square("h7"), "h8": Square("h8")}
