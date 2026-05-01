import boto3
import os

s3 = boto3.client(
        "s3",
        region_name = os.getenv("AWS_REGION"),
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key = os.getenv("AWS_SECRET_KEY")
    )

def uploadFiletoS3 (file, user_id: int, filename:str, folder:str):
    s3_key = f"{folder}/user_{user_id}/{filename}"

    s3.upload_fileobj (file, os.getenv("AWS_BUCKET_NAME"), s3_key)

    return s3_key 

def deleteFiletoS3 (s3_key:str):
    s3.delete_object(s3_key)

    return {"Notice" : "File deleted"}



    