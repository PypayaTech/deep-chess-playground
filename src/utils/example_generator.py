import pandas as pd
import random
import string
from datetime import datetime, timedelta
import chess
import chess.pgn
import zstandard as zstd
from src.utils.headers import HEADERS


class PgnZstGenerator:
    """
      Generates .pgn.zst and csv files for testing purposes and saves them in the specified directories

      Args:
        csv_destination_dir (str): Directory where the .csv files will be saved.
        pgn_destination_dir (str): Directory where the .pgn files will be saved.
        zst_destination_dir (str): Directory where the .pgn.zst files will be saved.
        comments (bool): Comments included
        num_games_per_file (int): Number of games
    """

    def __init__(self,
                 csv_destination_dir: str,
                 pgn_destination_dir: str,
                 zst_destination_dir: str,
                 comments: bool = False,
                 num_games_per_file: int = 5):
        self._csv_destination_dir = csv_destination_dir
        self._pgn_destination_dir = pgn_destination_dir
        self._zst_destination_dir = zst_destination_dir
        self._comments = comments
        self._num_games_per_file = num_games_per_file
        self._data = self._generate_data(num_games_per_file)

    def _generate_data(self, games: int) -> pd.DataFrame:
        data = []
        alphabet = string.ascii_lowercase

        for i in range(games):
            row = self._generate_game_data(i, alphabet)
            moves_str = self._generate_moves()
            row.append(moves_str)
            data.append(row)

        return pd.DataFrame(data, columns=HEADERS)

    def _generate_game_data(self, i: int, alphabet: str) -> list:
        return [
            f"Event {i}",
            'https://lichess.org/' + ''.join(random.choices(alphabet, k=10)),
            (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
            '-',
            ''.join(random.choices(alphabet, k=random.randint(1, 20))),
            ''.join(random.choices(alphabet, k=random.randint(1, 20))),
            random.choice(['1-0', '0-1', '1/2 1/2']),
            random.randint(100, 3000),
            random.randint(-99, 99),
            ''.join(random.choices(alphabet.upper() + '1234567890', k=3)),
            ''.join(random.choices(alphabet, k=random.randint(1, 20))),
            ''.join(random.choices(alphabet, k=random.randint(1, 20))),
            f"{random.randint(1, 999)}+{random.randint(1, 9)}",
            (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
            datetime.now().strftime('%H:%M:%S'),
            random.randint(100, 3000),
            random.randint(-99, 99)
        ]

    def _generate_moves(self) -> str:
        board = chess.Board()
        moves = []

        for _ in range(16):
            legal_moves = list(board.legal_moves)
            move = random.choice(legal_moves)
            moves.append(board.uci(move))
            board.push(move)

        return ' '.join(moves)

    # Return generated game as a csv file
    def to_csv(self):
        self._data.to_csv(self._csv_destination_dir, index=False)

    # Return the generated game as a compressed pgn file
    def to_pgn(self):
        pgn_list = []

        for index, row in self._data.iterrows():
            game = chess.pgn.Game()

            for header in self._data.columns:
                if header != 'Moves':
                    game.headers[header] = str(row[header])

            move_list = str(row['Moves']).split()
            node = game
            for move in move_list:
                node = node.add_variation(chess.Move.from_uci(move))
                if self._comments:
                    node.comment = self._generate_comment()

            pgn_list.append(str(game))

        pgn_str = "\n\n".join(pgn_list)
        with open(self._pgn_destination_dir, 'w') as file:
            file.write(pgn_str)

    def _generate_comment(self) -> str:
        score = round(random.uniform(-1, 1), 2)
        hour = random.randint(0, 9)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"[%eval {score}] [%clk {hour}:{minute:02d}:{second:02d}]"

    def to_zst(self):
        with open(self._pgn_destination_dir, 'rb') as infile:
            compressor = zstd.ZstdCompressor()
            compressed_data = compressor.compress(infile.read())
        with open(self._zst_destination_dir, 'wb') as outfile:
            outfile.write(compressed_data)

    # Return the generated game as a pandas dataframe
    @property
    def data(self) -> pd.DataFrame:
        return self._data

    def __str__(self) -> str:
        return self._data.to_string()

    def __eq__(self, other: pd.DataFrame) -> bool:
        return self._data.equals(other)
