from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import boto3
import os
from flask_wtf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()

# AWS S3 configuration (optional for development)
s3 = None
S3_BUCKET = None

csrf = CSRFProtect()
# Only initialize AWS if credentials are provided
if all(key in os.environ for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION', 'S3_BUCKET_NAME']):
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                          region_name=os.environ['AWS_REGION'])
        S3_BUCKET = os.environ['S3_BUCKET_NAME']
        print("✅ AWS S3 initialized successfully")
    except Exception as e:
        print(f"⚠️  AWS S3 initialization failed: {e}")
        s3 = None
        S3_BUCKET = None
else:
    print("ℹ️  AWS credentials not provided - S3 functionality disabled")