import boto3
import requests
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError
import os
import dotenv
import json
import uuid

# load into env variables located in aws_details in learner lab when you start it up
dotenv.load_dotenv()
REGION = os.getenv('REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

def get_client():
    """Helper function to create a client."""
    return boto3.client("s3",
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN, )

def create_bucket(bucket_name):
    s3 = get_client()
    try:
        s3.create_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False

def make_bucket_public(bucket_name):
    s3 = get_client()
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False
        }
    )
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }]
    }
    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(policy)
    )

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

def upload_image_from_url(bucket_name, url, object_name=None):
    s3 = get_client()
    if object_name is None:
        object_name = str(uuid.uuid4())
    response = requests.get(url)
    if response.status_code != 200:
        return False
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=response.content,
            ContentType=response.headers.get("Content-Type", "image/jpeg")
        )
        return True
    except ClientError:
        return False

# For testing purposes its going to be removed
# if __name__ == "__main__":
#     s3 = get_client()
#     print(s3.list_buckets())
#     print(create_bucket("jamell-test-bucket-123"))
#     print(make_bucket_public("jamell-test-bucket-123"))
#     print(s3.list_buckets())
#     upload_image("jamell-test-bucket-123", "../../tests/dog_test_image.avif")
#     upload_image_from_url("jamell-test-bucket-123","https://picsum.photos/id/1025/600/400")
#     print(list_images("jamell-test-bucket-123"))

#     # example link to access bucket https://jamell-test-bucket-123.s3.amazonaws.com/dog.jpg
#     delete_image("jamell-test-bucket-123", "dog_test_image.avif")
#     delete_image("jamell-test-bucket-123", "400")
#     print(delete_bucket("jamell-test-bucket-123"))
