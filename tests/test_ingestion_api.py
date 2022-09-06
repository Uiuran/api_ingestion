import datetime
from unittest.mock import mock_open, patch
from ingestion.ingestion_api import IngestorAPI
import pytest


@pytest.fixture
@patch("ingestion.ingestion_api.IngestorAPI.__abstractmethods__", set())
def ingestor_api_fixture():
    return IngestorAPI(coins=["TEST1", "TEST2"])


class TestIngestors:
    def test_checkpoint_filename(self, ingestor_api_fixture):
        actual = ingestor_api_fixture._checkpoint_filename
        expected = "IngestorAPI.checkpoint"
        assert actual == expected

    def test_load_checkpoint_no_checkpoint(self, ingestor_api_fixture):
        actual = ingestor_api_fixture._load_checkpoint()
        expected = None
        assert actual == expected

    @patch("builtins.open", new_callable=mock_open, read_data="2021-06-05")
    def test_load_checkpoint_exist_checkpoint(self, mock_open, ingestor_api_fixture):
        actual = ingestor_api_fixture._load_checkpoint()
        expected = datetime.date(2021, 6, 5)
        assert actual == expected

    @pytest.mark.parametrize("value", [datetime.date(2021, 2, 2)])
    def test_update_checkpoint(self, value, ingestor_api_fixture):
        actual = ingestor_api_fixture
        actual._update_checkpoint(value)
        expected = datetime.date(2021, 2, 2)
        assert actual._checkpoint == expected

    @patch("builtins.open", new_callable=mock_open)
    @patch(
        "ingestion.ingestion_api.IngestorAPI._checkpoint_filename",
        return_value="foo.checkpoint",
    )
    def test_write_checkpoint(self, mock_filename, mock_open, ingestor_api_fixture):
        ingestor_api_fixture._write_checkpoint()
        mock_open.assert_called_with(mock_filename, "w")
