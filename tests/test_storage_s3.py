import unittest
import boto3
from moto import mock_aws
import os
import uuid
import requests
from unittest.mock import patch, MagicMock

# Your actual module
from src.database import storageAws


@mock_aws
class TestStorageAws(unittest.TestCase):

    def setUp(self):
        """Spin up a mock S3 and create a dummy file before each test."""
        self.s3 = boto3.client("s3", region_name="us-east-1")
        self.bucket = "test-bucket"
        self.dummy_path = "dummy.jpg"
        with open(self.dummy_path, "wb") as f:
            f.write(b"fake image bytes")

    def tearDown(self):
        """Delete dummy file after tests."""
        if os.path.exists(self.dummy_path):
            os.remove(self.dummy_path)

    def test_create_bucket_success(self):
        self.assertTrue(storageAws.create_bucket(self.bucket))
        buckets = self.s3.list_buckets()
        self.assertIn(self.bucket, [b["Name"] for b in buckets["Buckets"]])

    def test_delete_bucket_success(self):
        self.s3.create_bucket(Bucket=self.bucket)
        self.assertTrue(storageAws.delete_bucket(self.bucket))
        buckets = self.s3.list_buckets()
        self.assertNotIn(self.bucket, [b["Name"] for b in buckets["Buckets"]])

    def test_delete_bucket_fail_not_empty(self):
        self.s3.create_bucket(Bucket=self.bucket)
        self.s3.put_object(Bucket=self.bucket, Key="file.txt", Body=b"")

        self.assertFalse(storageAws.delete_bucket(self.bucket))

    def test_upload_image_success(self):
        storageAws.create_bucket(self.bucket)
        result = storageAws.upload_image(self.bucket, self.dummy_path, "pic.jpg")
        self.assertTrue(result)

        objects = self.s3.list_objects_v2(Bucket=self.bucket)
        self.assertIn("pic.jpg", [o["Key"] for o in objects.get("Contents", [])])

    def test_upload_image_fail_bucket_missing(self):
        result = storageAws.upload_image("missing-bucket", self.dummy_path)
        self.assertFalse(result)

    def test_list_images(self):
        self.s3.create_bucket(Bucket=self.bucket)
        self.s3.put_object(Bucket=self.bucket, Key="a.jpg", Body=b"")
        self.s3.put_object(Bucket=self.bucket, Key="b.png", Body=b"")
        images = storageAws.list_images(self.bucket)
        self.assertEqual(len(images), 2)
        self.assertIn("a.jpg", images)

    def test_list_images_empty_bucket(self):
        self.s3.create_bucket(Bucket=self.bucket)
        self.assertEqual(storageAws.list_images(self.bucket), [])

    def test_list_images_bucket_missing(self):
        self.assertEqual(storageAws.list_images("nope"), [])

    def test_delete_image_success(self):
        self.s3.create_bucket(Bucket=self.bucket)
        self.s3.put_object(Bucket=self.bucket, Key="remove.jpg", Body=b"")

        self.assertTrue(storageAws.delete_image(self.bucket, "remove.jpg"))

        objs = self.s3.list_objects_v2(Bucket=self.bucket)
        self.assertNotIn("Contents", objs)

    @patch("requests.get")
    def test_upload_image_from_url_success(self, mock_get):
        """Mock URL download so tests don’t hit the internet."""
        storageAws.create_bucket(self.bucket)

        fake_resp = MagicMock()
        fake_resp.status_code = 200
        fake_resp.content = b"bytes from web"
        fake_resp.headers = {"Content-Type": "image/jpeg"}
        mock_get.return_value = fake_resp

        obj_name = str(uuid.uuid4())
        result = storageAws.upload_image_from_url(self.bucket, "http://fake", object_name=obj_name)

        self.assertTrue(result)
        objects = self.s3.list_objects_v2(Bucket=self.bucket)
        self.assertIn(obj_name, [o["Key"] for o in objects.get("Contents", [])])

    @patch("requests.get")
    def test_upload_image_from_url_404(self, mock_get):
        storageAws.create_bucket(self.bucket)
        fake_resp = MagicMock()
        fake_resp.status_code = 404
        mock_get.return_value = fake_resp
        result = storageAws.upload_image_from_url(self.bucket, "http://fake")
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()