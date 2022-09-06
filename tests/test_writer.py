from unittest.mock import mock_open, patch
from ingestion.api import DaySummary
from ingestion.writer import DataWriter
import pytest


class TestDataWriter:
    @pytest.mark.parametrize("data", [{"foo": "bar"}, [{"foo": "bar"}, {"abc": 123}]])
    @patch("builtins.open", new_callable=mock_open)
    def test_write(self, mock_open, data):
        actual = DataWriter(coin="TEST", api=DaySummary)
        actual.write(data)
        mock_open.assert_called_with(actual.filename, "a")
