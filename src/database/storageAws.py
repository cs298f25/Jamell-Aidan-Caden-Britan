import boto3
from botocore.exceptions import ClientError
import os
import dotenv
import json

dotenv.load_dotenv()
REGION = os.getenv('REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')


def get_client():
    return boto3.client("s3",
                        region_name=REGION,
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        aws_session_token=AWS_SESSION_TOKEN)


def create_bucket(bucket_name):
    s3 = get_client()
    try:
        s3.create_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {bucket_name} already exists.")
            return True
        print(f"Error creating bucket: {e}")
        return False


def make_bucket_public(bucket_name):
    """Makes the bucket publicly accessible with proper CORS and policy"""
    s3 = get_client()

    # Set CORS configuration
    cors_config = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE'],
            'AllowedOrigins': ['*'],
            'ExposeHeaders': []
        }]
    }

    try:
        s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_config)
        print(f"CORS configuration set for {bucket_name}")
    except ClientError as e:
        print(f"Error setting CORS: {e}")
        return False

    # Disable public access block
    try:
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": False,
                "IgnorePublicAcls": False,
                "BlockPublicPolicy": False,
                "RestrictPublicBuckets": False
            }
        )
        print(f"Public access block disabled for {bucket_name}")
    except ClientError as e:
        print(f"Error setting Public Access Block: {e}")
        return False

    # Set bucket policy for public read access
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }]
    }

    try:
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
        print(f"Bucket policy set for {bucket_name}")
        return True
    except ClientError as e:
        print(f"Error setting Bucket Policy: {e}")
        return False


def delete_bucket(bucket_name):
    s3 = get_client()
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            objects = [{'Key': obj['Key']} for obj in response['Contents']]
            s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})
        s3.delete_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            return True
        print(f"Error deleting bucket: {e}")
        return False


def upload_image_direct(bucket_name, file_stream, s3_key):
    s3 = get_client()
    try:
        s3.upload_fileobj(file_stream, bucket_name, s3_key)
        return True
    except ClientError as e:
        print(f"Failed to upload to S3: {e}")
        return False


def list_images_by_prefix(bucket_name, prefix):
    s3 = get_client()
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]
    except ClientError:
        return []


def list_images(bucket_name):
    return list_images_by_prefix(bucket_name, "")


def delete_image(bucket_name, object_name):
    s3 = get_client()
    try:
        s3.delete_object(Bucket=bucket_name, Key=object_name)
        return True
    except ClientError:
        return False


def get_images_by_user_and_category(bucket_name, username, category=None):
    prefix = f"{username}/{category}/" if category else f"{username}/"
    return list_images_by_prefix(bucket_name, prefix)