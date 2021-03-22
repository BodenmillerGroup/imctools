from pathlib import Path

from imctools.data import Session


class TestSession:
    def test_read_session(self, analysis_ometiff_path: Path):
        session_file_path = analysis_ometiff_path / '20210305_NE_mockData1' / '20210305_NE_mockData1_session.json'
        session = Session.load(session_file_path)
        assert session.name == "20210305_NE_mockData1"
        assert session.imctools_version == "2.1.4"
        assert session.id == "fea546d5-03dd-42ea-9871-eef63e9d1c79"
        assert list(session.slides.keys()) == [0]
        assert list(session.acquisitions.keys()) == [1, 2, 3]
        assert list(session.panoramas.keys()) == [1, 2]
