import logging
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from botocore.config import Config

load_dotenv()

def upload_file_to_s3(file_name, video_uuid):
    print(file_name)
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param video_uuid: UUID to use as the S3 object name
    :return: True if file was uploaded, else False
    """
    bucket_name = os.getenv("AWS_MP4_S3_BUCKET_ID")
    aws_region = os.getenv("AWS_REGION", "us-east-2")

    # Create an S3 client with signature version 4
    config = Config(signature_version='s3v4')
    s3_client = boto3.client('s3', config=config, region_name=aws_region)

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

def create_presigned_url(video_uuid):
    """Create a presigned URL for a video in S3"""
    bucket_name = os.getenv("AWS_MP4_S3_BUCKET_ID")
    aws_region = os.getenv("AWS_REGION", "us-east-2")

    print(video_uuid, bucket_name, aws_region)

    # Create an S3 client with signature version 4
    config = Config(signature_version='s3v4')
    s3_client = boto3.client('s3', config=config, region_name=aws_region)
    presigned_url = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': f'{video_uuid}.mp4'},
                                                    ExpiresIn=3600)
    print(presigned_url)
    return presigned_url