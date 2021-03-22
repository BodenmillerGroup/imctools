from pathlib import Path

from imctools.io.mcd.mcdparser import McdParser, McdXmlParser


class TestMcdXmlParser:
    def test_read_imc_mcd(self, raw_path: Path):
        mcd_file_path = raw_path / '20210305_NE_mockData1' / '20210305_NE_mockData1.mcd'
        mcd_parser = McdParser(mcd_file_path)
        xml = mcd_parser.get_mcd_xml()
        mcd_xml_parser = McdXmlParser(xml, str(mcd_file_path))
        assert mcd_xml_parser.session.name == "20210305_NE_mockData1"
