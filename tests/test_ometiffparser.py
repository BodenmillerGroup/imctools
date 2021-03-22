import pytest
from pathlib import Path

from imctools.io.ometiff.ometiffparser import OmeTiffParser


class TestOmeTiffParser:
    def test_read_invalid_suffix(self):
        with pytest.raises(FileNotFoundError):
            OmeTiffParser('file.unsupported_suffix')

    def test_read_ometiff(self, analysis_ometiff_path: Path):
        ometiff_file_path = analysis_ometiff_path / '20210305_NE_mockData1' / '20210305_NE_mockData1_s0_a1_ac.ome.tiff'
        parser = OmeTiffParser(ometiff_file_path)
        ac_data = parser.get_acquisition_data()
        assert parser.origin == "ome.tiff"
        assert ac_data.is_valid is True
        assert ac_data.image_data.shape == (5, 60, 60)
        assert ac_data.n_channels == 5
        assert ac_data.channel_names == ['Ag107', 'Pr141', 'Sm147', 'Eu153', 'Yb172']
        assert ac_data.channel_labels == ['107Ag', 'Cytoker_651((3356))Pr141', 'Laminin_681((851))Sm147', 'YBX1_2987((3532))Eu153', 'H3K27Ac_1977((2242))Yb172']
        assert ac_data.channel_masses == ['107', '141', '147', '153', '172']
