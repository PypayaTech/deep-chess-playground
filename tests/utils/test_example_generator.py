import pytest
import pandas as pd
from src.utils.example_generator import PgnZstGenerator
import os
from tests.utils.fixtures import tempdir, file_params


@pytest.mark.parametrize('use_comments, num_games', [
    (True, 5),
    (False, 3)
])
def test_generate_csv(tempdir, file_params, use_comments, num_games):
    csv_destination_dir, pgn_destination_dir, zst_destination_dir = file_params

    generator = PgnZstGenerator(csv_destination_dir, pgn_destination_dir, zst_destination_dir, use_comments, num_games)
    generator.to_csv()

    # Check that the csv file was generated and has the correct number of rows
    df = pd.read_csv(csv_destination_dir)
    assert len(df) == num_games


@pytest.mark.parametrize('use_comments, num_games', [
    (True, 5),
    (False, 3)
])
def test_generate_pgn(tempdir, file_params, use_comments, num_games):
    csv_destination_dir, pgn_destination_dir, zst_destination_dir = file_params

    generator = PgnZstGenerator(csv_destination_dir, pgn_destination_dir, zst_destination_dir, use_comments, num_games)
    generator.to_pgn()

    # Check that the pgn file was generated and has the correct number of games
    with open(pgn_destination_dir, 'r') as file:
        pgn_str = file.read()
        games = pgn_str.split('\n\n')
        assert len(games) == num_games * 2


@pytest.mark.parametrize('use_comments, num_games', [
    (True, 8),
    (False, 2)
])
def test_generate_zst(tempdir, file_params, use_comments, num_games):
    csv_destination_dir, pgn_destination_dir, zst_destination_dir = file_params
    num_games_per_file = 5
    comments = False

    generator = PgnZstGenerator(csv_destination_dir, pgn_destination_dir, zst_destination_dir, comments, num_games_per_file)
    generator.to_pgn()
    generator.to_zst()

    # Check that the zst file was generated and is not empty
    assert os.path.getsize(zst_destination_dir) > 0






import pytest
import pandas as pd
from src.utils.example_generator import PgnZstGenerator
import os
from tests.utils.fixtures import tempdir, file_params


@pytest.mark.parametrize('use_comments, num_games', [
    (True, 5),
    (False, 3)
])
def test_generate_csv(tempdir, file_params, use_comments, num_games):
    csv_destination_dir, pgn_destination_dir, zst_destination_dir = file_params

    generator = PgnZstGenerator(csv_destination_dir, pgn_destination_dir, zst_destination_dir, use_comments, num_games)
    generator.to_csv()

    # Check that the csv file was generated and has the correct number of rows
    df = pd.read_csv(csv_destination_dir)
    assert len(df) == num_games


@pytest.mark.parametrize('use_comments, num_games', [
    (True, 5),
    (False, 3)
])
def test_generate_pgn(tempdir, file_params, use_comments, num_games):
    csv_destination_dir, pgn_destination_dir, zst_destination_dir = file_params

    generator = PgnZstGenerator(csv_destination_dir, pgn_destination_dir, zst_destination_dir, use_comments, num_games)
    generator.to_pgn()

    # Check that the pgn file was generated and has the correct number of games
    with open(pgn_destination_dir, 'r') as file:
        pgn_str = file.read()
        games = pgn_str.split('\n\n')
        assert len(games) == num_games * 2


@pytest.mark.parametrize('use_comments, num_games', [
    (True, 8),
    (False, 2)
])
def test_generate_zst(tempdir, file_params, use_comments, num_games):
    csv_destination_dir, pgn_destination_dir, zst_destination_dir = file_params
    num_games_per_file = 5
    comments = False

    generator = PgnZstGenerator(csv_destination_dir, pgn_destination_dir, zst_destination_dir, comments, num_games_per_file)
    generator.to_pgn()
    generator.to_zst()

    # Check that the zst file was generated and is not empty
    assert os.path.getsize(zst_destination_dir) > 0






