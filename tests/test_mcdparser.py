import pytest
from pathlib import Path

from imctools.io.mcd.mcdparser import McdParser


class TestMcdParser:
    def test_read_invalid_suffix(self):
        with pytest.raises(FileNotFoundError):
            McdParser('file.unsupported_suffix')

    def test_read_imc_mcd(self, raw_path: Path):
        mcd_file_path = raw_path / '20210305_NE_mockData1' / '20210305_NE_mockData1.mcd'
        parser = McdParser(mcd_file_path)
        ac_data = parser.get_acquisition_data(1)
        assert parser.origin == "mcd"
        assert ac_data.is_valid is True
        assert ac_data.image_data.shape == (5, 60, 60)
        assert ac_data.n_channels == 5
        assert ac_data.channel_names == ['Ag107', 'Pr141', 'Sm147', 'Eu153', 'Yb172']
        assert ac_data.channel_labels == ['107Ag', 'Cytoker_651((3356))Pr141', 'Laminin_681((851))Sm147', 'YBX1_2987((3532))Eu153', 'H3K27Ac_1977((2242))Yb172']
        assert ac_data.channel_masses == ['107', '141', '147', '153', '172']
