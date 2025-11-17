# src/storageAws.py
import boto3
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError
import os
import dotenv


dotenv.load_dotenv()
REGION = os.getenv('REGION')

def get_client():
    """Helper function to create a client."""
    return boto3.client("s3", region_name=REGION)

def create_bucket(bucket_name):
    s3 = get_client()
    try:
        s3.create_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False

def delete_bucket(bucket_name):
    s3 = get_client()
    try:
        s3.delete_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False

def upload_image(bucket_name, file_path, object_name=None):
    s3 = get_client()
    if object_name is None:
        object_name = os.path.basename(file_path)
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        return True
    except (ClientError, S3UploadFailedError, FileNotFoundError):
        return False

def list_images(bucket_name):
    s3 = get_client()
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        return [obj['Key'] for obj in response.get('Contents', [])]
    except ClientError:
        return []

def delete_image(bucket_name, object_name):
    s3 = get_client()
    try:
        s3.delete_object(Bucket=bucket_name, Key=object_name)
        return True
    except ClientError:
        return False