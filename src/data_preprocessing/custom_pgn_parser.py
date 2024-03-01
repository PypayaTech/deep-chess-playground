import re
import io

HEADER_REGEX_dict = {
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

MOVE_REGEX = r'(O-O-O|O-O|[QKRBN]?([a-h]|[1-8])?x?[a-h][1-8]([#+]|=[QRBN][+#]?)?|1/2-1/2|1-0|0-1)'
GAME_REGEX = r'.*?\[Event.*?[^"](1/2-1/2|1-0|0-1|1/2 1/2)'


def custom_pgn_parser(stream: io.StringIO) -> dict:

    head_pos = stream.tell()
    string = stream.read()

    game = {}
    game_re = re.compile(GAME_REGEX, flags=re.DOTALL)

    game_raw = game_re.search(string)

    if game_raw is None: return None
    game_raw = string[game_raw.span()[0] : game_raw.span()[1]]    

    stream.seek(head_pos + len(game_raw))

    for h in HEADER_REGEX_dict:
        h_re = re.compile(HEADER_REGEX_dict[h])

        header_match = re.findall(h_re, game_raw)

        game[h] = header_match[0][1:-1] if len(header_match) > 0 else '?' 

    for line in game_raw.split('\n'):
        
        line = line.strip()
        if len(line) > 0 and line[0] == '1':

            occ = re.findall(MOVE_REGEX, line)
            game["Moves"] = ' '.join(move[0] for move in occ)

    return game
