import datetime
import json
from tempfile import NamedTemporaryFile
from typing import List, Union
from ingestion.Exceptions import WarningWrongDataTypeNotWritable
from ingestion.api import MercadoBitcoinAPI
from boto3 import Session
import os


class DataWriter:
    def __init__(self, coin: str, api: MercadoBitcoinAPI) -> None:
        self.api = api
        self.coin = coin
        self.partition = f"{coin}/{self.api.type}/"
        self.filename = self.partition + f"{datetime.datetime.now()}"

    def _write_row(self, row: str) -> None:
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, "a") as f:
            f.write(row)

    def _write_to_file(self, data: Union[List[dict], dict]):
        os.makedirs(self.partition, exist_ok=True)
        if isinstance(data, dict):
            self._write_row(json.dumps(data) + "\n")
        elif isinstance(data, list):
            for datum in data:
                if isinstance(datum, dict):
                    self._write_row(json.dumps(datum) + "\n")
                else:
                    warn = WarningWrongDataTypeNotWritable()
                    warn.warns(
                        f"Data type {datum.__class__} not allowed for writing, only dict is allowed. This datum will not be writed"
                    )

    def write(self, data: Union[List[dict], dict]) -> None:
        self._write_to_file(data)


# %%


class S3Writer(DataWriter):
    def __init__(
        self,
        coin: str,
        api: MercadoBitcoinAPI,
        profile_name: str = None,
        bucket: str = "demo-data-ingest-2",
    ):
        super().__init__(coin, api)
        self.temp_file = NamedTemporaryFile()
        self.bucket = bucket
        self.profile_name = profile_name
        if not profile_name:
            self.boto3_client = boto3.client("s3")
        else:
            self.boto3_client = Session(profile_name=profile_name).client("s3")
        self.key = f"mercadobitcoin/{self.api.__class__.__name__}/coin={self.coin}/extracted_at={datetime.datetime.now().date()}/mercadobitcoin_{datetime.datetime.now().date()}.json"

    def _write_row(self, row: str) -> None:
        with open(self.temp_file.name, "a") as f:
            f.write(row)

    def write(self, data: Union[List[dict], dict]) -> None:
        self._write_to_file(data)
        self._write_file_to_s3()

    def _write_file_to_s3(self) -> None:
        self.boto3_client.upload_file(
            Bucket=self.bucket, Filename=self.temp_file.name, Key=self.key
        )
