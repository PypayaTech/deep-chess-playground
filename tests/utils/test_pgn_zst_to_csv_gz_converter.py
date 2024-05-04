import pytest
import os
import gzip
import pandas as pd
from src.utils.pgn_zst_to_csv_gz_converter import PgnZstToCsvGzConverter
from src.dummy_generators.pgn_zst_generator import PgnZstGenerator
from tests.utils.fixtures import tempdir, file_params


@pytest.mark.parametrize('use_comments, num_games', [
    (True, 3),
    (False, 3)
])
def test_files_equal(tempdir, file_params, use_comments, num_games):
    csv_path, zst_path, pgn_path = file_params
    dtg = PgnZstGenerator(csv_path,
                          pgn_path,
                          zst_path,
                          use_comments,
                          num_games)
    dtg.to_pgn()
    dtg.to_zst()
    cnv = PgnZstToCsvGzConverter(zst_path, tempdir, num_games)
    cnv.convert()

    input_file = os.path.join(tempdir, '0.csv.gz')
    output_file = os.path.join(tempdir, '0_conv.csv')

    with gzip.open(input_file, 'rb') as f_in:
        # Read the contents of the file
        file_contents = f_in.read()

    with open(output_file, 'wb') as f_out:
        f_out.write(file_contents)

    df_converted = pd.read_csv(output_file)
    assert dtg == df_converted
