import logging
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def upload_file_to_s3(file_name, video_uuid):
    print(file_name)
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param video_uuid: UUID to use as the S3 object name
    :return: True if file was uploaded, else False
    """
    bucket_name = os.getenv("AWS_MP4_S3_BUCKET_ID")

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        s3_object_name = f"{video_uuid}.mp4"
        response = s3_client.upload_file(file_name, bucket_name, s3_object_name)
        logging.info(f"Successfully uploaded {file_name} to s3://{bucket_name}/{s3_object_name}")
        return True
    except ClientError as e:
        logging.error(e)
        return False

# Example usage:
if __name__ == "__main__":
    import uuid
    local_file_path = "BookmarkExample2.mp4"
    video_uuid = str(uuid.uuid4())

    if upload_file_to_s3(local_file_path, video_uuid):
        print("File uploaded successfully!")
    else:
        print("File upload failed.")
