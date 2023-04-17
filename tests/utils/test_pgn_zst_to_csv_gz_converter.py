import pytest
import os
import gzip
import pandas as pd
import shutil
from src.data_preprocessing.pgn_zst_to_csv_gz_converter import PgnZstToCsvGzConverter
from src.utils.example_generator import PgnZstGenerator


@pytest.fixture(scope="function")
def tempdir(request):
    tempdir_path = os.path.join(os.path.abspath("."), "tempdir")
    os.makedirs(tempdir_path)

    def teardown():
        shutil.rmtree(tempdir_path)

    request.addfinalizer(teardown)

    return tempdir_path


@pytest.mark.parametrize('use_comments, num_games', [
    (True, 3),
    (False, 3)
])
def test_files_equal(tempdir, use_comments, num_games):
    zst_path = os.path.join(tempdir, 'example_data.pgn.zst')
    dtg = PgnZstGenerator(os.path.join(tempdir, 'example_data.csv'),
                          os.path.join(tempdir, 'example_data.pgn'),
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
