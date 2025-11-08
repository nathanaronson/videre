import boto3
from botocore.exceptions import ClientError
import logging
from dotenv import load_dotenv
import os

load_dotenv()

def upload_file_to_s3(file_name, bucket_name, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket_name: S3 bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    if object_name is None:
        object_name = file_name

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
        logging.info(f"Successfully uploaded {file_name} to s3://{bucket_name}/{object_name}")
        return True
    except ClientError as e:
        logging.error(e)
        return False

# Example usage:
if __name__ == "__main__":
    local_file_path = "BookmarkExample2.mp4"
    s3_bucket = os.getenv("AWS_MP4_S3_BUCKET_ID")

    if upload_file_to_s3(local_file_path, s3_bucket):
        print("File uploaded successfully!")
    else:
        print("File upload failed.")