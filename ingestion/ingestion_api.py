# %%
from abc import ABC, abstractmethod
import datetime
import time
from timeit import repeat
from typing import List, Union
from ingestion.Exceptions import (
    StartDateNotProvidedException,
    WarningDateProvidedLowerThanCheckpoint,
)
from ingestion.api import DaySummary
from ingestion.checkpoints import CheckpointModel, DynamoCheckpoints
from ingestion.writer import DataWriter, S3Writer


class IngestorAPI(ABC):
    def __init__(self, coins: List[str]) -> None:
        super().__init__()
        self.coins = coins
        self._checkpoint = self._load_checkpoint()
        self.date = None

    @abstractmethod
    def ingestion(self, **kwargs) -> None:
        pass

    @property
    def _checkpoint_filename(self):
        return f"{self.__class__.__name__}.checkpoint"

    def _load_checkpoint(self) -> datetime.date:
        try:
            with open(self._checkpoint_filename, "r") as f:
                return datetime.datetime.strptime(f.read(), "%Y-%m-%d").date()
        except:
            return None

    def _write_checkpoint(self):

        with open(self._checkpoint_filename, "w") as f:
            f.write(f"{self._checkpoint}")

    def _get_checkpoint(self) -> Union[datetime.date, datetime.datetime]:

        if not self._checkpoint:
            return self.date
        else:

            return self._checkpoint

    def _update_checkpoint(
        self, value: Union[datetime.date, datetime.datetime]
    ) -> None:
        self._checkpoint = value


# %%


class DaySummaryIngestor(IngestorAPI):
    def ingestion(
        self, date: datetime.date = None, data_writer: DataWriter = S3Writer, **kwargs
    ) -> None:
        if not date and not self._checkpoint:
            raise StartDateNotProvidedException(
                "Start date is None and there is no checkpoint, an initial value must be provided"
            )
        elif not date and self._checkpoint:
            self.date = self._get_checkpoint()
        else:

            if not self._checkpoint:
                self.date = date
            elif date >= self._checkpoint:
                self.date = date
            elif date < self._checkpoint:
                warn = WarningDateProvidedLowerThanCheckpoint()
                warn.warns(
                    f"{date} is lower than {self._checkpoint}, using checkpoint instead. If you want to restart the ingestion you must delete the checkpoint"
                )
                self.date = self._get_checkpoint()

        if self.date < datetime.date.today():
            for coin in self.coins:
                day_summary = DaySummary(coin=coin)
                writer = data_writer(coin=coin, api=day_summary, **kwargs)
                writer.write(day_summary.get_data(date=self.date))
            self._update_checkpoint(self.date + datetime.timedelta(days=1))
            self._write_checkpoint()


class AwsDataIngestor:
    def __init__(self, writer, coins: List[str], default_start_date:
            datetime.date, profile_name: str = None) -> None:
        self.dynamo_checkpoint = DynamoCheckpoints(
            model=CheckpointModel,
            report_id=self.__class__.__name__,
            default_start_date=default_start_date)
        self.default_start_date = default_start_date
        self.coins = coins
        self.writer = writer
        self._checkpoint = self._load_checkpoint()
        self.profile_name = profile_name


    def _write_checkpoint(self):
        self.dynamo_checkpoint.create_checkpoint(checkpoint_date=self._checkpoint)

    def _load_checkpoint(self) -> datetime.date:
        return self.dynamo_checkpoint.get_checkpoint()

    def _update_checkpoint(self, value):
        self._checkpoint = value
        self.dynamo_checkpoint.create_or_update_checkpoint(checkpoint_date=self._checkpoint)

    @abstractmethod
    def ingest(self) -> None:
        pass


class AwsDaySummaryIngestor(AwsDataIngestor):

    def ingest(self) -> None:
        date = self._load_checkpoint()
        if date < datetime.datetime.now(datetime.timezone.utc).date():
            for coin in self.coins:
                api = DaySummary(coin=coin)
                data = api.get_data(date=date)
                if not self.profile_name:
                    self.writer(coin=coin, api=api).write(data)
                else:
                    self.writer(coin=coin, api=api,
                            profile_name=self.profile_name).write(data)
            self._update_checkpoint(date + datetime.timedelta(days=1))
