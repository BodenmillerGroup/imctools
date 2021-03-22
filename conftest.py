import pytest
import requests
import shutil
from pathlib import Path


def _download_and_extract_asset(tmp_dir_path: Path, asset_url: str):
    asset_file_path = tmp_dir_path / 'asset.tar.gz'
    response = requests.get(asset_url, stream=True)
    if response.status_code == 200:
        with asset_file_path.open(mode='wb') as f:
            f.write(response.raw.read())
    shutil.unpack_archive(asset_file_path, tmp_dir_path)


@pytest.fixture(scope='session')
def analysis_cpout_images_path(tmp_path_factory):
    tmp_dir_path: Path = tmp_path_factory.mktemp('analysis_cpout_images')
    _download_and_extract_asset(tmp_dir_path, 'https://github.com/BodenmillerGroup/TestData/releases/download/v1.0.1/210308_ImcTestData_analysis_cpout_images.tar.gz')
    yield tmp_dir_path / 'datasets' / '210308_ImcTestData' / 'analysis' / 'cpout' / 'images'
    shutil.rmtree(tmp_dir_path)


@pytest.fixture(scope='session')
def analysis_cpout_masks_path(tmp_path_factory):
    tmp_dir_path: Path = tmp_path_factory.mktemp('analysis_cpout_images')
    _download_and_extract_asset(tmp_dir_path, 'https://github.com/BodenmillerGroup/TestData/releases/download/v1.0.1/210308_ImcTestData_analysis_cpout_masks.tar.gz')
    yield tmp_dir_path / 'datasets' / '210308_ImcTestData' / 'analysis' / 'cpout' / 'masks'
    shutil.rmtree(tmp_dir_path)


@pytest.fixture(scope='session')
def analysis_ometiff_path(tmp_path_factory):
    tmp_dir_path: Path = tmp_path_factory.mktemp('analysis_ometiff')
    _download_and_extract_asset(tmp_dir_path, 'https://github.com/BodenmillerGroup/TestData/releases/download/v1.0.1/210308_ImcTestData_analysis_ometiff.tar.gz')
    yield tmp_dir_path / 'datasets' / '210308_ImcTestData' / 'analysis' / 'ometiff'
    shutil.rmtree(tmp_dir_path)


@pytest.fixture(scope='session')
def raw_path(tmp_path_factory):
    tmp_dir_path: Path = tmp_path_factory.mktemp('raw')
    _download_and_extract_asset(tmp_dir_path, 'https://github.com/BodenmillerGroup/TestData/releases/download/v1.0.1/210308_ImcTestData_raw.tar.gz')
    yield tmp_dir_path / 'datasets' / '210308_ImcTestData' / 'raw'
    shutil.rmtree(tmp_dir_path)
