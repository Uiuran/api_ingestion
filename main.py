# %%
import datetime
import time
from ingestion.writer import S3Writer

from ingestion.ingestion_api import AwsDaySummaryIngestor, DaySummaryIngestor


if __name__ == "__main__":
    ingestor = AwsDaySummaryIngestor(S3Writer,["ETH", "BTC", "LTC"],default_start_date=datetime.date(2022,1,5))

    while True:
        ingestor.ingest()
        time.sleep(0.5)

# %%
