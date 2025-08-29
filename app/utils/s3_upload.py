import boto3
import os
from fastapi import UploadFile, HTTPException
from typing import Optional
import uuid
from datetime import datetime
from app.core.config import settings

class S3UploadService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is required")

    async def upload_file(self, file: UploadFile, folder: str = "uploads") -> str:
        """
        Upload file to S3 and return the URL
        """
        try:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
            unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
            
            # Upload file to S3
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                unique_filename,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'ACL': 'public-read'
                }
            )
            
            # Generate public URL
            file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{unique_filename}"
            
            return file_url
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to S3: {str(e)}"
            )
        finally:
            file.file.close()

    async def delete_file(self, file_url: str) -> bool:
        """
        Delete file from S3
        """
        try:
            # Extract key from URL
            key = file_url.replace(f"https://{self.bucket_name}.s3.amazonaws.com/", "")
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except Exception as e:
            print(f"Failed to delete file from S3: {str(e)}")
            return False

    def is_valid_image(self, file: UploadFile) -> bool:
        """
        Check if uploaded file is a valid image
        """
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        return file.content_type in allowed_types

    def get_file_size_mb(self, file: UploadFile) -> float:
        """
        Get file size in MB
        """
        file.file.seek(0, 2)  # Seek to end
        size_bytes = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        return size_bytes / (1024 * 1024)


# Global instance
s3_service = S3UploadService()
