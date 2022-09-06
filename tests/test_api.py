# %%
import datetime
from unittest.mock import patch
from ingestion.api import DaySummary, MercadoBitcoinAPI, Trades
from ingestion.Exceptions import DateDataIngestionNotFoundException
import requests
import pytest


class TestDaySummary:
    @pytest.mark.parametrize(
        "coin,date,expected",
        [
            (
                "BTC",
                datetime.date(2022, 6, 2),
                "https://www.mercadobitcoin.net/api/BTC/day-summary/2022/6/2",
            ),
            (
                "ETH",
                datetime.date(2021, 4, 23),
                "https://www.mercadobitcoin.net/api/ETH/day-summary/2021/4/23",
            ),
        ],
    )
    def test_get_endpoint(self, coin, date, expected):
        day_summary = DaySummary(coin=coin)
        actual = day_summary._get_endpoint(date=date)
        assert actual == expected


# %%


class TestTrades:
    @pytest.mark.parametrize(
        "coin, date_from, date_to, expected",
        [
            (
                "BTC",
                datetime.datetime(2021, 2, 20),
                datetime.datetime(2022, 1, 5),
                "https://www.mercadobitcoin.net/api/BTC/trades/1613779200/1641340800",
            ),
            (
                "BTC",
                datetime.datetime(2021, 2, 20),
                None,
                "https://www.mercadobitcoin.net/api/BTC/trades/1613779200",
            ),
        ],
    )
    def test_get_endpoint(self, coin, date_from, date_to, expected):
        actual = Trades(coin=coin)._get_endpoint(date_start=date_from, date_to=date_to)
        assert actual == expected

    @pytest.mark.parametrize(
        "coin, date_start, date_to",
        [("BTC", None, datetime.datetime(2021, 2, 20)), ("BTC", None, None)],
    )
    def test_get_endpoint_none_at_date_start_exception(self, coin, date_start, date_to):
        with pytest.raises(DateDataIngestionNotFoundException):
            Trades(coin=coin)._get_endpoint(date_start=date_start, date_to=date_to)

    @pytest.mark.parametrize(
        "coin, date, expected", [("BTC", datetime.datetime(2022, 1, 5), 1641340800)]
    )
    def test_get_unix_date(self, coin, date, expected):
        actual = Trades(coin=coin)._get_unix_date(date=date)
        assert actual == expected


@pytest.fixture
@patch("ingestion.api.MercadoBitcoinAPI.__abstractmethods__", set())
def mercado_bitcoin_fixture():
    return MercadoBitcoinAPI(coin="TEST")


def mocked_requests_get(*args, **kwargs):
    class MockResponse(requests.Response):
        def __init__(self, json_data, status_code):
            super().__init__()
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception

    if args[0] == "valid_endpoint":
        return MockResponse(json_data={"foo": "bar"}, status_code=200)
    else:
        return MockResponse(json_data=None, status_code=404)


class TestMercadoBitcoinAPI:
    @patch("requests.get")
    @patch("ingestion.api.MercadoBitcoinAPI._get_endpoint", return_value="foobar/")
    def test_get_data(self, mock_get_endpoint, mock_requests, mercado_bitcoin_fixture):
        mercado_bitcoin_fixture.get_data()
        mock_requests.assert_called_once_with(mock_get_endpoint())

    @patch("requests.get", side_effect=mocked_requests_get)
    @patch(
        "ingestion.api.MercadoBitcoinAPI._get_endpoint", return_value="valid_endpoint"
    )
    def test_get_data_valid_endpoint(
        self, mock_requests_get, mock_get_endpoint, mercado_bitcoin_fixture
    ):
        actual = mercado_bitcoin_fixture.get_data()
        expected = {"foo": "bar"}
        actual == expected

    @patch("requests.get", side_effect=mocked_requests_get)
    @patch(
        "ingestion.api.MercadoBitcoinAPI._get_endpoint", return_value="invalid_endpoint"
    )
    def test_get_data_invalid_endpoint(
        self, mock_requests_get, mock_get_endpoint, mercado_bitcoin_fixture
    ):
        with pytest.raises(Exception):
            mercado_bitcoin_fixture.get_data()

def test_fail():
    assert False 