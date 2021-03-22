from pathlib import Path

from imctools.io.imc.imcparser import ImcParser


class TestImcParser:
    def test_read_imc_folder(self, analysis_ometiff_path: Path):
        imc_folder_path = analysis_ometiff_path / '20210305_NE_mockData1'
        parser = ImcParser(imc_folder_path)
        ac_data = parser.get_acquisition_data(1)
        assert parser.origin == "imc"
        assert ac_data.is_valid is True
        assert ac_data.image_data.shape == (5, 60, 60)
        assert ac_data.n_channels == 5
        assert ac_data.channel_names == ['Ag107', 'Pr141', 'Sm147', 'Eu153', 'Yb172']
        assert ac_data.channel_labels == ['107Ag', 'Cytoker_651((3356))Pr141', 'Laminin_681((851))Sm147', 'YBX1_2987((3532))Eu153', 'H3K27Ac_1977((2242))Yb172']
        assert ac_data.channel_masses == ['107', '141', '147', '153', '172']

    def test_read_img(self, analysis_ometiff_path: Path):
        imc_folder_path = analysis_ometiff_path / '20210305_NE_mockData1'
        parser = ImcParser(imc_folder_path)
        ac_data = parser.get_acquisition_data(1)
        img = ac_data.get_image_by_name('Ag107')
        assert img.shape == (60, 60)
