import boto3
from botocore.exceptions import ClientError
import os
import dotenv

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


def generate_presigned_url(bucket_name, s3_key, expiration=604800):
    """Generate a pre-signed URL for an S3 object (default 7 days)"""
    s3 = get_client()
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None


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