import io
from typing import Optional, Dict, List, Tuple
import re
from src.utils.headers import HEADERS


class PythonChessPGNParser:
    def __init__(self):
        import chess.pgn
        self.chess_pgn = chess.pgn

    def parse(self, stream: io.StringIO) -> Optional[tuple]:
        game = self.chess_pgn.read_game(stream)
        if game is None:
            return None
        game_info = [game.headers.get(key, '?') for key in HEADERS[:-1]]
        mainline_moves = " ".join([str(move) for move in game.mainline_moves()])
        return game_info, mainline_moves


class PGNParser:
    def __init__(self):
        self.header_regexes = {
            'Event': re.compile(r'\[Event\s+"(.*)"\]'),
            'Site': re.compile(r'\[Site\s+"(.*)"\]'),
            'Date': re.compile(r'\[Date\s+"(.*)"\]'),
            'Round': re.compile(r'\[Round\s+"(.*)"\]'),
            'White': re.compile(r'\[White\s+"(.*)"\]'),
            'Black': re.compile(r'\[Black\s+"(.*)"\]'),
            'Result': re.compile(r'\[Result\s+"(.*)"\]'),
            'UTCDate': re.compile(r'\[UTCDate\s+"(.*)"\]'),
            'UTCTime': re.compile(r'\[UTCTime\s+"(.*)"\]'),
            'WhiteElo': re.compile(r'\[WhiteElo\s+"(.*)"\]'),
            'BlackElo': re.compile(r'\[BlackElo\s+"(.*)"\]'),
            'WhiteRatingDiff': re.compile(r'\[WhiteRatingDiff\s+"(.*)"\]'),
            'BlackRatingDiff': re.compile(r'\[BlackRatingDiff\s+"(.*)"\]'),
            'ECO': re.compile(r'\[ECO\s+"(.*)"\]'),
            'Opening': re.compile(r'\[Opening\s+"(.*)"\]'),
            'TimeControl': re.compile(r'\[TimeControl\s+"(.*)"\]'),
            'Termination': re.compile(r'\[Termination\s+"(.*)"\]')
        }
        self.comment_regex = re.compile(r'\{[^}]\}|;.*$')
        self.variation_regex = re.compile(r'\([^)]*\)')
        self.move_regex = re.compile(r'(?:\d+\.+\s)?([PNBRQK]?[a-h]?[1-8]?x?[a-h][1-8](?:=[NBRQ])?|O-O(?:-O)?|0-0(?:-0)?|[PNBRQK][a-h1-8]?x?[a-h][1-8]?|[a-h]x?[a-h][1-8](?:=[NBRQ])?)(?:[+#]?)(?:\s[!?]+)?')

    def parse(self, stream: io.StringIO) -> Optional[tuple]:
        return self.parse_game_custom(stream)

    def parse_game_custom(self, stream: io.StringIO) -> Optional[tuple]:
        headers, start_of_moves = self.parse_headers(stream)

        stream.seek(start_of_moves)
        moves = self.parse_moves(stream)

        # Create game_info list with correct order based on HEADERS
        game_info = [headers.get(header, '?') for header in HEADERS[:-1]]  # Exclude 'Moves' from HEADERS

        # If no moves were found, set moves to an empty string
        if not moves:
            moves = ""

        return game_info, moves

    def parse_headers(self, stream: io.StringIO) -> Tuple[Dict[str, str], int]:
        headers = {}
        start_of_moves = stream.tell()  # Initialize to current position
        for line in stream:
            line = line.strip()
            if not line:
                continue
            if line[0] != '[':
                break
            for key, regex in self.header_regexes.items():
                match = regex.match(line)
                if match:
                    headers[key] = match.group(1)
                    break
            start_of_moves = stream.tell()  # Update after each header line
        return headers, start_of_moves

    def parse_moves(self, stream: io.StringIO) -> str:
        movetext = stream.read()

        # Remove comments and variations
        movetext = self.comment_regex.sub('', movetext)
        movetext = self.variation_regex.sub('', movetext)

        # Extract moves
        moves = self.move_regex.findall(movetext)

        # Remove game termination marker
        if moves and moves[-1] in {'1-0', '0-1', '1/2-1/2', '*'}:
            moves.pop()

        result = " ".join(moves)
        return result
