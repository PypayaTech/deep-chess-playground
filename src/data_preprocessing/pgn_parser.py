import re
import io
from typing import Optional
import chess
from src.utils.headers import HEADERS


class PGNParser:
    def __init__(self, use_python_chess=True):
        self.use_python_chess = use_python_chess
        self.HEADER_REGEX_dict = {
            'Event': r'\[Event (?P<Event>\".*\")\]',
            'Site': r'\[Site (?P<Site>\".*\")\]',
            'Date': r'\[Date (?P<Date>\".*\")\]',
            'Round': r'\[Round (?P<Round>\".*\")\]',
            'White': r'\[White (?P<White>\".*\")\]',
            'Black': r'\[Black (?P<Black>\".*\")\]',
            'Result': r'\[Result (?P<Result>\".*\")\]',
            'BlackElo': r'\[BlackElo (?P<BlackElo>\".*\")\]',
            'BlackRatingDiff': r'\[BlackRatingDiff (?P<BlackRatingDiff>\".*\")\]',
            'ECO': r'\[ECO (?P<ECO>\".*\")\]',
            'Opening': r'\[Opening (?P<Opening>\".*\")\]',
            'Termination': r'\[Termination (?P<Termination>\".*\")\]',
            'TimeControl': r'\[TimeControl (?P<TimeControl>\".*\")\]',
            'UTCDate': r'\[UTCDate (?P<UTCDate>\".*\")\]',
            'UTCTime': r'\[UTCTime (?P<UTCTime>\".*\")\]',
            'WhiteElo': r'\[WhiteElo (?P<WhiteElo>\".*\")\]',
            'WhiteRatingDiff': r'\[WhiteRatingDiff (?P<WhiteRatingDiff>\".*\")\]'
        }
        self.MOVE_REGEX = r'(O-O-O|O-O|[QKRBN]?([a-h]|[1-8])?x?[a-h][1-8]([#+]|=[QRBN][+#]?)?|1/2-1/2|1-0|0-1)'
        self.GAME_REGEX = r'.*?\[Event.*?[^"](1/2-1/2|1-0|0-1|1/2 1/2)'

    @staticmethod
    def parse(stream: io.StringIO, use_python_chess=True):
        parser = PGNParser(use_python_chess)
        return parser.parse_game(stream)

    def parse_game(self, stream: io.StringIO) -> Optional[tuple]:
        if self.use_python_chess:
            game = chess.pgn.read_game(stream)
            if game is None:
                return None
            game_info = [game.headers.get(key, '?') for key in HEADERS[:-1]]
            mainline_moves = " ".join([str(move) for move in game.mainline_moves()])
        else:
            game = self.custom_parse(stream)
            if game is None:
                return None
            game_info = [game[key] for key in HEADERS[:-1]]
            mainline_moves = game["Moves"]
        return game_info, mainline_moves

    def custom_parse(self, stream: io.StringIO) -> dict:
        head_pos = stream.tell()
        string = stream.read()

        game = {}
        game_re = re.compile(self.GAME_REGEX, flags=re.DOTALL)

        game_raw = game_re.search(string)

        if game_raw is None: return None
        game_raw = string[game_raw.span()[0]: game_raw.span()[1]]

        stream.seek(head_pos + len(game_raw))

        for h in self.HEADER_REGEX_dict:
            h_re = re.compile(self.HEADER_REGEX_dict[h])

            header_match = re.findall(h_re, game_raw)

            game[h] = header_match[0][1:-1] if len(header_match) > 0 else '?'

        for line in game_raw.split('\n'):

            line = line.strip()
            if len(line) > 0 and line[0] == '1':
                occ = re.findall(self.MOVE_REGEX, line)
                game["Moves"] = ' '.join(move[0] for move in occ)

        return game
