import pytest
from pathlib import Path

from imctools.io.txt.txtparser import TxtParser


class TestTxtParser:
    def test_read_invalid_suffix(self):
        with pytest.raises(FileNotFoundError):
            TxtParser('file.unsupported_suffix')

    def test_read_ometiff(self, raw_path: Path):
        txt_file_path = raw_path / '20210305_NE_mockData1' / '20210305_NE_mockData1_ROI_001_1.txt'
        parser = TxtParser(txt_file_path)
        ac_data = parser.get_acquisition_data()
        assert parser.origin == "txt"
        assert ac_data.is_valid is True
        assert ac_data.image_data.shape == (5, 60, 60)
        assert ac_data.n_channels == 5
        assert ac_data.channel_names == ['Ag107', 'Pr141', 'Sm147', 'Eu153', 'Yb172']
        assert ac_data.channel_labels == ['107Ag(Ag107Di)', 'Cytoker_651((3356))Pr141(Pr141Di)', 'Laminin_681((851))Sm147(Sm147Di)', 'YBX1_2987((3532))Eu153(Eu153Di)', 'H3K27Ac_1977((2242))Yb172(Yb172Di)']
        assert ac_data.channel_masses == ['107', '141', '147', '153', '172']
