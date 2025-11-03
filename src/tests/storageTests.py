import unittest
import boto3
from moto import mock_aws
import os
from src import storageAws


class TestStorageAws(unittest.TestCase):

    @mock_aws
    def setUp(self):
        """Set up a mocked S3 environment before each test"""
        self.s3_client = boto3.client("s3", region_name="us-east-1")
        self.bucket_name = "my-test-bucket"

        # Create a dummy file for upload tests
        self.dummy_file_path = "test_image.jpg"
        with open(self.dummy_file_path, "wb") as f:
            f.write(b"fake image data")

    def tearDown(self):
        """Clean up dummy file after each test"""
        if os.path.exists(self.dummy_file_path):
            os.remove(self.dummy_file_path)

    @mock_aws
    def test_create_bucket_success(self):
        result = storageAws.create_bucket(self.bucket_name)
        self.assertTrue(result)
        response = self.s3_client.list_buckets()
        self.assertIn(self.bucket_name, [b['Name'] for b in response['Buckets']])

    @mock_aws
    def test_upload_image_success(self):
        storageAws.create_bucket(self.bucket_name)
        object_name = "new_image.jpg"
        result = storageAws.upload_image(self.bucket_name, self.dummy_file_path, object_name)
        self.assertTrue(result)
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        self.assertIn(object_name, [obj['Key'] for obj in response['Contents']])

    @mock_aws
    def test_upload_image_fail_no_bucket(self):
        result = storageAws.upload_image("non-existent-bucket", self.dummy_file_path)
        self.assertFalse(result)

    @mock_aws
    def test_list_images_success(self):
        self.s3_client.create_bucket(Bucket=self.bucket_name)
        self.s3_client.put_object(Bucket=self.bucket_name, Key="img1.jpg", Body=b"")
        self.s3_client.put_object(Bucket=self.bucket_name, Key="img2.png", Body=b"")

        images = storageAws.list_images(self.bucket_name)

        self.assertEqual(len(images), 2)
        self.assertIn("img1.jpg", images)

    @mock_aws
    def test_list_images_empty_bucket(self):
        self.s3_client.create_bucket(Bucket=self.bucket_name)
        images = storageAws.list_images(self.bucket_name)
        self.assertEqual(images, [])

    @mock_aws
    def test_list_images_fail_no_bucket(self):
        images = storageAws.list_images("non-existent-bucket")
        self.assertEqual(images, [])

    @mock_aws
    def test_delete_image_success(self):
        self.s3_client.create_bucket(Bucket=self.bucket_name)
        object_name = "image_to_delete.jpg"
        self.s3_client.put_object(Bucket=self.bucket_name, Key=object_name, Body=b"")
        result = storageAws.delete_image(self.bucket_name, object_name)
        self.assertTrue(result)
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        self.assertNotIn('Contents', response)

    @mock_aws
    def test_delete_bucket_success(self):
        self.s3_client.create_bucket(Bucket=self.bucket_name)
        result = storageAws.delete_bucket(self.bucket_name)
        self.assertTrue(result)
        response = self.s3_client.list_buckets()
        self.assertNotIn(self.bucket_name, [b['Name'] for b in response['Buckets']])

    @mock_aws
    def test_delete_bucket_fail_not_empty(self):
        self.s3_client.create_bucket(Bucket=self.bucket_name)
        self.s3_client.put_object(Bucket=self.bucket_name, Key="file.txt", Body=b"")
        result = storageAws.delete_bucket(self.bucket_name)
        self.assertFalse(result)
        response = self.s3_client.list_buckets()
        self.assertIn(self.bucket_name, [b['Name'] for b in response['Buckets']])


if __name__ == '__main__':
    unittest.main()