import io
import os.path
import logging
from collections import deque
from typing import List
from queue import Queue
import zstandard as zstd
import pandas as pd
import threading
from pypaya_pgn_parser.pgn_parser import PGNParser
from deep_chess_playground.utils.headers import HEADERS


CHUNK_SIZE = 1024 * 1024
CHUNKS_QUEUE_SIZE = 1024
GAMES_QUEUE_SIZE = 1024 * 1024


# Set up logging
logging.basicConfig(filename='pgn_zst_to_csv_gz_converter.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PgnZstToCsvGzConverter:
    """Converts compressed .pgn.zst files to compressed .csv.gz files on the fly.

        Args:
            pgn_zst_path (str): Path to the .pgn.zst file.
            destination_dir (str): Directory where the .csv files will be saved.
            num_games_per_file (int): Maximum number of games per .csv file.
            chunk_size (int): Size of a single read from the source file.
            separator(str): separator used in .csv files.
        """

    def __init__(self,
                 pgn_zst_path: str,
                 destination_dir: str,
                 num_games_per_file: int,
                 chunk_size: int = CHUNK_SIZE,
                 separator: str = ',',
                 use_python_chess=True):
        self._pgn_zst_path = pgn_zst_path
        self._destination_dir = destination_dir
        self._num_games_per_file = num_games_per_file
        self._chunk_size = chunk_size
        self._separator = separator
        self._chunks_queue = Queue(maxsize=CHUNKS_QUEUE_SIZE)
        self._games_queue = Queue(maxsize=GAMES_QUEUE_SIZE)
        self._end_of_data = False
        self._csv_file_counter = 0
        self._use_python_chess = use_python_chess
        self._parser = PGNParser()
        logging.info(f"Initialized PgnZstToCsvGzConverter with file: {pgn_zst_path}")

    def convert(self):
        """Starts reading and writing threads."""
        logging.info("Starting conversion process")
        read_zst_thread = threading.Thread(target=self._read_zst, args=())
        write_csv_gz_thread = threading.Thread(target=self._write_csv_gz, args=())
        write_games_thread = threading.Thread(target=self._write_games, args=())
        read_zst_thread.start()
        write_csv_gz_thread.start()
        write_games_thread.start()
        read_zst_thread.join()
        write_csv_gz_thread.join()
        write_games_thread.join()
        logging.info("Conversion process completed")

    def _read_zst(self):
        """Reads data from the .pgn.zst file and adds it to the chunks queue."""
        logging.info(f"Starting to read {self._pgn_zst_path}")
        with open(self._pgn_zst_path, 'rb') as f:
            reader = zstd.ZstdDecompressor().stream_reader(f)
            chunk = reader.read(self._chunk_size)
            chunks_read = 0
            while chunk:
                self._chunks_queue.put(chunk)
                chunk = reader.read(self._chunk_size)
                chunks_read += 1
                if chunks_read % 100 == 0:
                    logging.info(f"Read {chunks_read} chunks")
            # Put a sentinel value in the queue to signal the end of the data
            self._chunks_queue.put(None)
        logging.info(f"Finished reading {self._pgn_zst_path}")

    def _write_csv_gz(self,):
        """Takes the data from the queue and writes it to the .csv.gz file."""
        logging.info("Starting to parse games")
        two_last_positions = deque([0], maxlen=2)
        remaining_part = ""
        current_games = []
        data = self._chunks_queue.get()
        games_parsed = 0
        while data is not None:
            string = remaining_part + data.decode("utf-8")
            stream = io.StringIO(string)
            current_games = []
            result = self._parser.parse(stream)
            data = None
            while result is not None:
                game_info, mainline_moves = result
                current_games.append(game_info + [mainline_moves])
                two_last_positions.append(stream.tell())
                result = self._parser.parse(stream)
                games_parsed += 1
                if games_parsed % 1000 == 0:
                    logging.info(f"Parsed {games_parsed} games")
            for item in current_games[:-1]:
                self._games_queue.put(item)
            remaining_part = string[two_last_positions[0]:]
            data = self._chunks_queue.get()
        if current_games:
            self._games_queue.put(current_games[-1])
        self._end_of_data = True
        logging.info(f"Finished parsing games. Total games parsed: {games_parsed}")

    def _write_games(self):
        """Reads the games from the games queue and saves them to a disk
        every num_games_per_file files."""
        logging.info("Starting to write games to CSV")
        games = []
        while not self._end_of_data:
            games.append(self._games_queue.get())
            if len(games) == self._num_games_per_file:
                self._save_games_on_disk(games)
                games = []
        games.extend([game for game in self._games_queue.queue])
        for i in range(int(len(games) / self._num_games_per_file) + 1):
            self._save_games_on_disk(games[i * self._num_games_per_file: (i + 1) * self._num_games_per_file])
        logging.info(f"Finished writing games to CSV.")

    def _save_games_on_disk(self, games: List[str]):
        """Creates dataframe from the list of lists of strings and saves it to the .csv file."""
        filepath = os.path.join(self._destination_dir, f"{self._csv_file_counter}.csv.gz")
        logging.info(f"Saving games to file {filepath}")
        df = pd.DataFrame(games, columns=HEADERS)
        df.to_csv(filepath, index=False, compression="infer", sep=self._separator)
        self._csv_file_counter += 1
        logging.info(f"Games saved to file {filepath}")
