import io
import os.path
import logging
from collections import deque
from typing import List, Optional
from queue import Queue, Empty
import zstandard as zstd
import pandas as pd
import threading
from pypaya_pgn_parser.pgn_parser import PGNParser
from deep_chess_playground.utils.headers import HEADERS


# Constants
CHUNK_SIZE = 1024 * 1024
CHUNKS_QUEUE_SIZE = 1024
GAMES_QUEUE_SIZE = 1024 * 1024
QUEUE_TIMEOUT = 1
LOG_INTERVAL = 100
ENCODING = 'utf-8'


# Set up logging
logging.basicConfig(filename='pgn_zst_to_csv_gz_converter.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PgnZstToCsvGzConverter:
    """Converts compressed .pgn.zst files to compressed .csv.gz files on the fly.

    This class reads a Zstandard-compressed PGN (Portable Game Notation) file,
    parses the chess games within, and writes them to CSV (Comma-Separated Values)
    files compressed with gzip. It uses a multi-threaded approach for efficient
    processing of large files.

    Args:
        pgn_zst_path (str): Path to the input .pgn.zst file.
        destination_dir (str): Directory where the output .csv.gz files will be saved.
        num_games_per_file (int): Maximum number of games to include in each output file.
        chunk_size (int, optional): Size of each chunk read from the input file. Defaults to CHUNK_SIZE.
        separator (str, optional): Separator to use in the CSV files. Defaults to ','.

    Attributes:
        _pgn_zst_path (str): Path to the input .pgn.zst file.
        _destination_dir (str): Directory where output .csv.gz files are saved.
        _num_games_per_file (int): Maximum number of games per .csv.gz file.
        _chunk_size (int): Size of a single read from the source file.
        _separator (str): Separator used in .csv files.
        _chunks_queue (Queue): Queue for storing file chunks.
        _games_queue (Queue): Queue for storing parsed games.
        _end_of_data (bool): Flag indicating end of input data.
        _csv_file_counter (int): Counter for generated CSV files.
        _parser (PGNParser): Parser object for PGN data.

    Raises:
        FileNotFoundError: If the input file or destination directory doesn't exist.
        PermissionError: If there's no write permission for the destination directory.
        ValueError: If the input file is empty.
        RuntimeError: If an error occurs during the conversion process.

    Example:
        converter = PgnZstToCsvGzConverter('games.pgn.zst', 'output_dir', 1000)
        converter.convert()
    """

    def __init__(
            self,
            pgn_zst_path: str,
            destination_dir: str,
            num_games_per_file: int,
            chunk_size: int = CHUNK_SIZE,
            separator: str = ','
    ):
        self._validate_inputs(pgn_zst_path, destination_dir)

        self._pgn_zst_path = pgn_zst_path
        self._destination_dir = destination_dir
        self._num_games_per_file = num_games_per_file
        self._chunk_size = chunk_size
        self._separator = separator
        self._chunks_queue: Queue = Queue(maxsize=CHUNKS_QUEUE_SIZE)
        self._games_queue: Queue = Queue(maxsize=GAMES_QUEUE_SIZE)
        self._end_of_data = False
        self._csv_file_counter = 0
        self._parser = PGNParser()

        logging.info(f"Initialized PgnZstToCsvGzConverter with file: {pgn_zst_path}")

    @staticmethod
    def _validate_inputs(pgn_zst_path: str, destination_dir: str) -> None:
        """Validate input file and destination directory."""
        if not os.path.exists(pgn_zst_path):
            raise FileNotFoundError(f"Input file not found: {pgn_zst_path}")
        if not os.path.exists(destination_dir):
            raise FileNotFoundError(f"Destination directory not found: {destination_dir}")
        if not os.access(destination_dir, os.W_OK):
            raise PermissionError(f"No write permission for destination directory: {destination_dir}")
        if os.path.getsize(pgn_zst_path) == 0:
            raise ValueError(f"Input file is empty: {pgn_zst_path}")

    def convert(self) -> None:
        """Starts reading and writing threads."""
        logging.info("Starting conversion process")
        try:
            threads = [
                threading.Thread(target=self._read_zst),
                threading.Thread(target=self._write_csv_gz),
                threading.Thread(target=self._write_games)
            ]

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            logging.info("Conversion process completed")
        except Exception as e:
            logging.error(f"Error during conversion process: {e}")
            raise RuntimeError(f"Conversion process failed: {e}")

    def _read_zst(self) -> None:
        """Reads data from the .pgn.zst file and adds it to the chunks queue."""
        logging.info(f"Starting to read {self._pgn_zst_path}")
        try:
            with open(self._pgn_zst_path, 'rb') as f:
                reader = zstd.ZstdDecompressor().stream_reader(f)
                chunks_read, total_bytes_read = 0, 0

                while chunk := reader.read(self._chunk_size):
                    self._chunks_queue.put(chunk)
                    chunks_read += 1
                    total_bytes_read += len(chunk)

                    if chunks_read % LOG_INTERVAL == 0:
                        logging.debug(f"Read {chunks_read} chunks, total bytes: {total_bytes_read}")

                self._chunks_queue.put(None)  # Sentinel value
                logging.info(
                    f"Finished reading {self._pgn_zst_path}. Total chunks: {chunks_read}, total bytes: {total_bytes_read}")
        except Exception as e:
            logging.error(f"Error reading input file: {e}")
            self._chunks_queue.put(None)
            raise

    def _write_csv_gz(self) -> None:
        """Takes the data from the queue and writes it to the .csv.gz file."""
        logging.info("Starting to parse games")
        two_last_positions = deque([0], maxlen=2)
        remaining_part = ""
        games_parsed, chunk_count = 0, 0

        while data := self._get_next_chunk():
            chunk_count += 1
            string = self._process_chunk(remaining_part, data)
            stream = io.StringIO(string)
            current_games = self._parse_games(stream, two_last_positions)

            self._add_games_to_queue(current_games)
            games_parsed += len(current_games)

            if games_parsed % LOG_INTERVAL == 0:
                logging.info(f"Parsed {games_parsed} games")

            remaining_part = string[two_last_positions[0]:]

        self._end_of_data = True
        logging.info(f"Finished parsing games. Total games parsed: {games_parsed}")
        logging.debug(f"Total chunks processed: {chunk_count}")

    def _get_next_chunk(self) -> Optional[bytes]:
        """Get the next chunk from the queue."""
        try:
            return self._chunks_queue.get(timeout=QUEUE_TIMEOUT)
        except Empty:
            return None

    @staticmethod
    def _process_chunk(remaining_part: str, data: bytes) -> str:
        """Process the chunk data."""
        return remaining_part + data.decode(ENCODING).replace('\r\n', '\n').replace('\r', '\n')

    def _parse_games(self, stream: io.StringIO, two_last_positions: deque) -> List[List[str]]:
        """Parse games from the given stream."""
        current_games = []
        while result := self._parser.parse(stream):
            game_info, mainline_moves = result
            if game_info and mainline_moves:
                current_games.append(game_info + [mainline_moves])
            else:
                logging.warning(f"Empty game detected. Game info: {game_info}, Moves: {mainline_moves}")
            two_last_positions.append(stream.tell())
        return current_games

    def _add_games_to_queue(self, games: List[List[str]]) -> None:
        """Add parsed games to the games queue."""
        for game in games[:-1]:
            self._games_queue.put(game)
        if games:
            self._games_queue.put(games[-1])

    def _write_games(self) -> None:
        """Reads the games from the games queue and saves them to a disk."""
        logging.info("Starting to write games to CSV")
        games, games_written = [], 0

        while not self._end_of_data or not self._games_queue.empty():
            game = self._get_next_game()
            if game:
                games.append(game)
                if len(games) == self._num_games_per_file:
                    self._save_games_on_disk(games)
                    games_written += len(games)
                    games = []
                    logging.debug(f"Written {games_written} games so far")

        if games:
            self._save_games_on_disk(games)
            games_written += len(games)

        logging.info(f"Finished writing games to CSV. Total games written: {games_written}")

    def _get_next_game(self) -> Optional[List[str]]:
        """Get the next game from the queue."""
        try:
            return self._games_queue.get(timeout=QUEUE_TIMEOUT)
        except Empty:
            return None

    def _save_games_on_disk(self, games: List[List[str]]) -> None:
        """Creates dataframe from the list of lists of strings and saves it to the .csv file."""
        if not games:
            logging.info("No games to save, skipping file creation")
            return

        filepath = os.path.join(self._destination_dir, f"{self._csv_file_counter}.csv.gz")
        logging.info(f"Saving games to file {filepath}")
        try:
            df = pd.DataFrame(games, columns=HEADERS)
            df.to_csv(filepath, index=False, compression="infer", sep=self._separator)
            self._csv_file_counter += 1
            logging.info(f"Games saved to file {filepath}")
        except Exception as e:
            logging.error(f"Error saving games to file: {e}")
            raise
