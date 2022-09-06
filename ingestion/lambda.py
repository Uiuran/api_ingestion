from datetime import datetime
from ingestion.ingestion_api import AwsDaySummaryIngestor
from ingestion.writer import S3Writer
import datetime
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    logger.info(f"{event}")
    logger.info(f"{context}")
    
    AwsDaySummaryIngestor(
        writer = S3Writer,
        coins = ["BTC","ETH","LTC"],
        default_start_date= datetime.date(2022,6,1)
    ).ingest()