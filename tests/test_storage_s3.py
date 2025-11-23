import pytest
import boto3
from moto import mock_aws
from io import BytesIO
from src.database import storageAws

@pytest.fixture
def s3_client():
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")

@pytest.fixture
def bucket_name():
    return "test-bucket"

@mock_aws
def test_create_bucket_works(s3_client, bucket_name):
    assert storageAws.create_bucket(bucket_name)
    buckets = s3_client.list_buckets()
    assert bucket_name in [b["Name"] for b in buckets["Buckets"]]

@mock_aws
def test_delete_empty_bucket_works(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    assert storageAws.delete_bucket(bucket_name)
    buckets = s3_client.list_buckets()
    assert bucket_name not in [b["Name"] for b in buckets["Buckets"]]

@mock_aws
def test_delete_bucket_with_objects_works(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.put_object(Bucket=bucket_name, Key="file.txt", Body=b"")
    assert storageAws.delete_bucket(bucket_name)
    buckets = s3_client.list_buckets()
    assert bucket_name not in [b["Name"] for b in buckets["Buckets"]]

@mock_aws
def test_upload_direct_works(s3_client, bucket_name):
    storageAws.create_bucket(bucket_name)
    file_stream = BytesIO(b"test content")
    result = storageAws.upload_image_direct(bucket_name, file_stream, "test.jpg")
    assert result
    objects = s3_client.list_objects_v2(Bucket=bucket_name)
    assert "test.jpg" in [o["Key"] for o in objects.get("Contents", [])]

@mock_aws
def test_upload_direct_fails_missing_bucket():
    file_stream = BytesIO(b"test content")
    result = storageAws.upload_image_direct("missing-bucket", file_stream, "test.jpg")
    assert not result

@mock_aws
def test_list_images_returns_all(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.put_object(Bucket=bucket_name, Key="a.jpg", Body=b"")
    s3_client.put_object(Bucket=bucket_name, Key="b.png", Body=b"")
    images = storageAws.list_images(bucket_name)
    assert len(images) == 2
    assert "a.jpg" in images

@mock_aws
def test_list_images_empty_bucket(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    assert storageAws.list_images(bucket_name) == []

@mock_aws
def test_list_images_missing_bucket():
    assert storageAws.list_images("nope") == []

@mock_aws
def test_list_images_by_prefix(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.put_object(Bucket=bucket_name, Key="user1/photo.jpg", Body=b"")
    s3_client.put_object(Bucket=bucket_name, Key="user2/photo.jpg", Body=b"")
    images = storageAws.list_images_by_prefix(bucket_name, "user1/")
    assert len(images) == 1
    assert "user1/photo.jpg" in images

@mock_aws
def test_delete_image_works(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.put_object(Bucket=bucket_name, Key="remove.jpg", Body=b"")
    assert storageAws.delete_image(bucket_name, "remove.jpg")
    objs = s3_client.list_objects_v2(Bucket=bucket_name)
    assert "Contents" not in objs

@mock_aws
def test_get_images_by_user_and_category(s3_client, bucket_name):
    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.put_object(Bucket=bucket_name, Key="alice/designs/logo.png", Body=b"")
    s3_client.put_object(Bucket=bucket_name, Key="alice/photos/pic.jpg", Body=b"")
    images = storageAws.get_images_by_user_and_category(bucket_name, "alice", "designs")
    assert len(images) == 1
    assert "alice/designs/logo.png" in images