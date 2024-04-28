import shutil
import pytest
import os


@pytest.fixture(scope="function")
def tempdir(request):
    tempdir_path = os.path.join(os.path.abspath("."), "tempdir")
    if not os.path.isdir(tempdir_path):
        os.makedirs(tempdir_path)

    def teardown():
        shutil.rmtree(tempdir_path)

    request.addfinalizer(teardown)

    return tempdir_path


@pytest.fixture(scope="function")
def file_params(tempdir):
    csv_destination_dir = os.path.join(tempdir, 'example_data.csv')
    pgn_destination_dir = os.path.join(tempdir, 'example_data.pgn')
    zst_destination_dir = os.path.join(tempdir, 'example_data.pgn.zst')
    return csv_destination_dir, pgn_destination_dir, zst_destination_dir
