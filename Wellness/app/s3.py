import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException
from io import BytesIO

def upload_image_to_s3(image_bytes: BytesIO, bucket_name: str, file_name: str) -> str:   
    s3 = boto3.client('s3') 
    try:
        s3.upload_fileobj(image_bytes, bucket_name, file_name)
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        return image_url
    except Exception as e:
        raise Exception(f"Failed to upload file to S3: {str(e)}")