import os
import pytest
import tempfile
import pandas as pd
import zstandard as zstd
from deep_chess_playground.utils.pgn_zst_to_csv_gz_converter import PgnZstToCsvGzConverter


@pytest.fixture
def sample_pgn_zst_file():
    with tempfile.NamedTemporaryFile(suffix='.pgn.zst', delete=False) as temp_file:
        # Create a sample .pgn.zst file with a few games
        sample_pgn_content = """[Event "Example Game 1"]
[Site "Online"]
[Date "2023.09.18"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0

[Event "Example Game 2"]
[Site "Online"]
[Date "2023.09.18"]
[Round "2"]
[White "Player3"]
[Black "Player4"]
[Result "0-1"]

1. d4 d5 2. c4 e6 3. Nc3 Nf6 0-1
"""
        compressed = zstd.compress(sample_pgn_content.encode('utf-8'))
        temp_file.write(compressed)
    return temp_file.name


@pytest.fixture
def output_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def example_pgn_zst_file(tmp_path):
    # Path to your example.pgn file in the tests/data directory
    example_pgn_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'example.pgn')

    # Create a temporary .pgn.zst file
    temp_zst_path = tmp_path / "example.pgn.zst"

    # Read the content of example.pgn and compress it
    with open(example_pgn_path, 'rb') as f:
        content = f.read()

    compressed = zstd.compress(content)

    # Write the compressed content to the temporary .pgn.zst file
    with open(temp_zst_path, 'wb') as f:
        f.write(compressed)

    return str(temp_zst_path)


def test_pgn_zst_to_csv_gz_conversion(sample_pgn_zst_file, output_dir):
    converter = PgnZstToCsvGzConverter(
        pgn_zst_path=sample_pgn_zst_file,
        destination_dir=output_dir,
        num_games_per_file=10
    )
    converter.convert()

    # Check if the output file was created
    output_files = os.listdir(output_dir)
    assert len(output_files) == 1
    assert output_files[0].endswith('.csv.gz')

    # Read the output file and check its content
    output_file_path = os.path.join(output_dir, output_files[0])
    df = pd.read_csv(output_file_path, compression='gzip')

    # Check if the DataFrame has the expected number of rows (games)
    assert len(df) == 2

    # Check if the DataFrame has the expected columns
    expected_columns = ['Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Result', 'Moves']
    assert all(col in df.columns for col in expected_columns)

    # Check some values in the DataFrame
    assert df.loc[0, 'Event'] == 'Example Game 1'
    assert df.loc[1, 'Event'] == 'Example Game 2'
    assert df.loc[0, 'Result'] == '1-0'
    assert df.loc[1, 'Result'] == '0-1'


def test_invalid_input_file(output_dir):
    with pytest.raises(FileNotFoundError):
        PgnZstToCsvGzConverter(
            pgn_zst_path='nonexistent_file.pgn.zst',
            destination_dir=output_dir,
            num_games_per_file=10
        )


def test_invalid_output_directory(sample_pgn_zst_file):
    with pytest.raises(FileNotFoundError):
        converter = PgnZstToCsvGzConverter(
            pgn_zst_path=sample_pgn_zst_file,
            destination_dir='/nonexistent/directory',
            num_games_per_file=10
        )
        converter.convert()


def test_empty_input_file(output_dir):
    with tempfile.NamedTemporaryFile(suffix='.pgn.zst', delete=False) as temp_file:
        temp_file.write(b'')  # Write an empty file

    with pytest.raises(ValueError, match="Input file is empty"):
        PgnZstToCsvGzConverter(
            pgn_zst_path=temp_file.name,
            destination_dir=output_dir,
            num_games_per_file=10
        )


def test_large_num_games_per_file(sample_pgn_zst_file, output_dir):
    converter = PgnZstToCsvGzConverter(
        pgn_zst_path=sample_pgn_zst_file,
        destination_dir=output_dir,
        num_games_per_file=1000  # Larger than the number of games in the sample file
    )
    converter.convert()

    output_files = os.listdir(output_dir)
    assert len(output_files) == 1  # Should create only one file


def test_example_pgn_conversion(example_pgn_zst_file, output_dir):
    converter = PgnZstToCsvGzConverter(
        pgn_zst_path=example_pgn_zst_file,
        destination_dir=output_dir,
        num_games_per_file=100  # Adjust this as needed
    )
    converter.convert()

    # Check if the output files were created
    output_files = sorted(os.listdir(output_dir))
    assert len(output_files) > 0
    assert all(file.endswith('.csv.gz') for file in output_files)

    # Read all output files and concatenate them
    dfs = []
    for file in output_files:
        df = pd.read_csv(os.path.join(output_dir, file), compression='gzip')
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)

    # Check if we have the expected number of games
    assert len(combined_df) == 54

    # Check if the DataFrame has the expected columns
    expected_columns = ['Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Result', 'Moves']
    assert all(col in combined_df.columns for col in expected_columns)

    # Check some known values from the games:
    assert combined_df.loc[1, 'Event'] == 'Rated Bullet tournament https://lichess.org/tournament/yc1WW2Ox'
    assert combined_df.loc[1, 'White'] == 'Abbot'

    # Check that all games have moves
    assert combined_df['Moves'].notna().all()

    # Check that all games have a valid result
    assert combined_df['Result'].isin(['1-0', '0-1', '1/2-1/2', '*']).all()
