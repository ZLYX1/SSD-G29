from flask_sqlalchemy import SQLAlchemy
import boto3
import os
from flask_wtf import CSRFProtect

db = SQLAlchemy()

s3 = boto3.client('s3',
                  aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                  region_name=os.environ['AWS_REGION'])

S3_BUCKET = os.environ['S3_BUCKET_NAME']

csrf = CSRFProtect()
