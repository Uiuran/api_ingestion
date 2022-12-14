# %%
import datetime
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
import pynamodb.connection
import logging
from boto3 import Session
import boto3

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
#%%
session = Session(profile_name="awsadm")
#%%
class CheckpointModel(Model):
    class Meta:
        aws_access_key_id = session.get_credentials().access_key
        aws_secret_access_key = session.get_credentials().secret_key
        table_name = "mercado_bitcoin_ingestor_checkpoints"
        region = "sa-east-1"

    report_id = UnicodeAttribute(hash_key=True)
    checkpoint_date = UnicodeAttribute()


class DynamoCheckpoints:
    def __init__(self, model: Model, report_id: str, default_start_date: datetime.date):
        self.model = model
        self.report_id = report_id
        self.default_start_date = default_start_date
        self.create_table()

    def create_checkpoint(self, checkpoint_date: str):
        checkpoint = self.model(self.report_id, checkpoint_date=f"{checkpoint_date}")
        checkpoint.save()

    def update_checkpoint(self, checkpoint_date: str):
        checkpoint = self.model.get(self.report_id)
        checkpoint.checkpoint_date = f"{checkpoint_date}"
        checkpoint.save()
        
    def get_checkpoint(self):
        
        if self.checkpoint_exist:
            checkpoint = list(self.model.query(self.report_id))[0].checkpoint_date
            logger.info(f"Checkpoint found for {self.report_id}:{checkpoint}")
            return datetime.datetime.strptime(checkpoint,"%Y-%m-%d").date()
        else:
            logger.info(f"Checkpoint not founnd for {self.report_id}, using default_start_date {self.default_start_date}")
            return self.default_start_date

    def create_or_update_checkpoint(self, checkpoint_date):
        logger.info(f"Saving checkpoint for {self.report_id}:{checkpoint_date}")
        if not self.checkpoint_exist:
            self.create_checkpoint(checkpoint_date)
        else:
            self.update_checkpoint(checkpoint_date)

    @property
    def checkpoint_exist(self):
        try:
            return list(self.model.query(self.report_id)) != []
        except KeyError:
            logger.warning(f"KeyError: {self.report_id}")
            return False

    def create_table(self):
        logger.info(f"Creating DynamoDB Table")
        if not self.model.exists():
            self.model.create_table(billing_mode="PAY_PER_REQUEST", wait=True)


# %%
DB = DynamoCheckpoints(
    model=CheckpointModel, report_id="abc", default_start_date=datetime.date(2020, 1, 5)
)

DB.create_table()
# %%
