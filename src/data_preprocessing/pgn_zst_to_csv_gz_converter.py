import io
import os.path
from collections import deque
import chess
import chess.pgn
from queue import Queue
import zstandard as zstd
import pandas as pd
import threading


CHUNK_SIZE = 1024 * 1024
CHUNKS_QUEUE_SIZE = 1024
GAMES_QUEUE_SIZE = 1024 * 1024


class PgnZstToCsvGzConverter:
    """Converts compressed .pgn.zst files to compressed .csv.gz files on the fly.

        Args:
            pgn_zst_path (str): Path to the .pgn.zst file.
            destination_dir (str): Directory where the .csv files will be saved.
            num_games_per_file (int): Maximum number of games per .csv file.
            chunk_size (int): Size of a single read from the source file.
        """

    def __init__(self,
                 pgn_zst_path: str,
                 destination_dir: str,
                 num_games_per_file: int,
                 chunk_size: int = CHUNK_SIZE):
        self._pgn_zst_path = pgn_zst_path
        self._destination_dir = destination_dir
        self._num_games_per_file = num_games_per_file
        self._chunk_size = chunk_size
        self._chunks_queue = Queue(maxsize=CHUNKS_QUEUE_SIZE)
        self._games_queue = Queue(maxsize=GAMES_QUEUE_SIZE)
        self._end_of_data = False
        self._csv_file_counter = 0
        self._headers = ['Event',
                         'Site',
                         'Date',
                         'Round',
                         'White',
                         'Black',
                         'Result',
                         'BlackElo',
                         'BlackRatingDiff',
                         'ECO',
                         'Opening',
                         'Termination',
                         'TimeControl',
                         'UTCDate',
                         'UTCTime',
                         'WhiteElo',
                         'WhiteRatingDiff',
                         'Moves']

    def convert(self):
        """Starts reading and writing threads."""
        read_zst_thread = threading.Thread(target=self._read_zst, args=())
        write_csv_gz_thread = threading.Thread(target=self._write_csv_gz, args=())
        write_games_thread = threading.Thread(target=self._write_games, args=())
        read_zst_thread.start()
        write_csv_gz_thread.start()
        write_games_thread.start()
        read_zst_thread.join()
        write_csv_gz_thread.join()
        write_games_thread.join()

    def _read_zst(self):
        """Reads data from the .pgn.zst file and adds it to the chunks queue."""
        with open(self._pgn_zst_path, 'rb') as f:
            reader = zstd.ZstdDecompressor().stream_reader(f)
            chunk = reader.read(self._chunk_size)
            while chunk:
                self._chunks_queue.put(chunk)
                chunk = reader.read(self._chunk_size)
            # Put a sentinel value in the queue to signal the end of the data
            self._chunks_queue.put(None)

    def _write_csv_gz(self):
        """Takes the data from the queue and writes it to the .csv.gz file."""
        two_last_positions = deque([0], maxlen=2)
        remaining_part = ""
        current_games = []
        data = self._chunks_queue.get()
        while data is not None:
            string = remaining_part + data.decode("utf-8")
            stream = io.StringIO(string)
            current_games = []
            game = chess.pgn.read_game(stream)
            while game is not None:
                game_info = [game.headers.get(key, '?') for key in self._headers[:-1]]
                mainline_moves = " ".join([str(move) for move in game.mainline_moves()])
                current_games.append(game_info + [mainline_moves])
                two_last_positions.append(stream.tell())
                game = chess.pgn.read_game(stream)
            for item in current_games[:-1]:
                self._games_queue.put(item)
            remaining_part = string[two_last_positions[0]:]
            data = self._chunks_queue.get()
        self._games_queue.put(current_games[-1])
        self._end_of_data = True

    def _write_games(self):
        """Reads the games from the games queue and saves them to a disk
        every num_games_per_file files."""
        games = []
        while not self._end_of_data:
            games.append(self._games_queue.get())
            if len(games) == self._num_games_per_file:
                self._save_games_on_disk(games)
                games = []
        games.extend([game for game in self._games_queue.queue])
        for i in range(int(len(games) / self._num_games_per_file) + 1):
            self._save_games_on_disk(games[i * self._num_games_per_file: (i + 1) * self._num_games_per_file])

    def _save_games_on_disk(self, games: list[str]):
        """Creates dataframe from the list of lists of strings and saves it to the .csv file."""
        filepath = os.path.join(self._destination_dir, f"{self._csv_file_counter}.csv.gz")
        print(f"Saving games to a file {filepath}.")
        df = pd.DataFrame(games, columns=self._headers)
        df.to_csv(filepath, index=False, compression="infer", sep='\t')
        self._csv_file_counter += 1
        print(f"Games saved to a file {filepath}.")
