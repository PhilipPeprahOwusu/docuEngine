"""Cloud Storage Service for Document Upload/Download"""
import os
import uuid
from typing import BinaryIO, Optional
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """Unified storage service supporting GCP Cloud Storage, AWS S3, and local storage"""

    def __init__(self, provider: str = "gcp"):
        """
        Initialize storage service

        Args:
            provider: Storage provider (gcp, aws, local)
        """
        self.provider = provider.lower()
        self.client = None

        if self.provider == "gcp":
            self._init_gcp()
        elif self.provider == "aws":
            self._init_aws()
        elif self.provider == "local":
            self._init_local()
        else:
            raise ValueError(f"Unsupported storage provider: {provider}")

    def _init_gcp(self):
        """Initialize GCP Cloud Storage client"""
        try:
            from google.cloud import storage
            from app.core.config import settings

            # Use Application Default Credentials (works with Workload Identity on GKE)
            self.client = storage.Client(project=settings.GCP_PROJECT_ID)
            self.bucket_name = settings.GCS_BUCKET
            logger.info(f"Initialized GCP Cloud Storage with bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GCP storage: {e}")
            # Fallback to local storage if GCP init fails
            logger.warning("Falling back to local storage")
            self.provider = "local"
            self._init_local()

    def _init_aws(self):
        """Initialize AWS S3 client"""
        try:
            import boto3
            from app.core.config import settings

            self.client = boto3.client('s3', region_name=settings.AWS_REGION)
            self.bucket_name = settings.S3_BUCKET
            logger.info(f"Initialized AWS S3 with bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize AWS storage: {e}")
            logger.warning("Falling back to local storage")
            self.provider = "local"
            self._init_local()

    def _init_local(self):
        """Initialize local file storage"""
        self.local_storage_path = "/tmp/docuengine_uploads"
        os.makedirs(self.local_storage_path, exist_ok=True)
        logger.info(f"Initialized local storage at: {self.local_storage_path}")

    async def upload_file(
        self,
        file: UploadFile,
        object_name: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> tuple[str, bytes]:
        """
        Upload a file to cloud storage

        Args:
            file: FastAPI UploadFile object
            object_name: Optional custom object name (defaults to generated UUID)
            org_id: Organization ID for folder organization

        Returns:
            Tuple of (storage_key, file_content_bytes)
        """
        # Read file content
        content = await file.read()

        # Generate object name if not provided
        if not object_name:
            file_extension = os.path.splitext(file.filename)[1]
            object_name = f"{uuid.uuid4()}{file_extension}"

        # Add org_id folder if provided
        if org_id:
            storage_key = f"{org_id}/{object_name}"
        else:
            storage_key = object_name

        # Upload based on provider
        if self.provider == "gcp":
            self._upload_gcp(storage_key, content, file.content_type)
        elif self.provider == "aws":
            self._upload_aws(storage_key, content, file.content_type)
        elif self.provider == "local":
            self._upload_local(storage_key, content)

        logger.info(f"Uploaded file to {self.provider}: {storage_key}")
        return storage_key, content

    def _upload_gcp(self, object_name: str, content: bytes, content_type: str):
        """Upload to GCP Cloud Storage"""
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(object_name)
            blob.upload_from_string(content, content_type=content_type)
        except Exception as e:
            logger.error(f"GCP upload failed: {e}")
            raise

    def _upload_aws(self, object_name: str, content: bytes, content_type: str):
        """Upload to AWS S3"""
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=content,
                ContentType=content_type
            )
        except Exception as e:
            logger.error(f"AWS upload failed: {e}")
            raise

    def _upload_local(self, object_name: str, content: bytes):
        """Upload to local filesystem"""
        file_path = os.path.join(self.local_storage_path, object_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(content)

    def download_file(self, storage_key: str) -> bytes:
        """
        Download a file from cloud storage

        Args:
            storage_key: The storage key/path of the file

        Returns:
            File content as bytes
        """
        if self.provider == "gcp":
            return self._download_gcp(storage_key)
        elif self.provider == "aws":
            return self._download_aws(storage_key)
        elif self.provider == "local":
            return self._download_local(storage_key)

    def _download_gcp(self, object_name: str) -> bytes:
        """Download from GCP Cloud Storage"""
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(object_name)
        return blob.download_as_bytes()

    def _download_aws(self, object_name: str) -> bytes:
        """Download from AWS S3"""
        response = self.client.get_object(Bucket=self.bucket_name, Key=object_name)
        return response['Body'].read()

    def _download_local(self, object_name: str) -> bytes:
        """Download from local filesystem"""
        file_path = os.path.join(self.local_storage_path, object_name)
        with open(file_path, 'rb') as f:
            return f.read()

    def get_file_url(self, storage_key: str) -> str:
        """
        Get the URL for a stored file

        Args:
            storage_key: The storage key/path of the file

        Returns:
            Public or signed URL for the file
        """
        if self.provider == "gcp":
            return f"gs://{self.bucket_name}/{storage_key}"
        elif self.provider == "aws":
            return f"s3://{self.bucket_name}/{storage_key}"
        elif self.provider == "local":
            return f"file://{self.local_storage_path}/{storage_key}"

    def delete_file(self, storage_key: str):
        """
        Delete a file from cloud storage

        Args:
            storage_key: The storage key/path of the file
        """
        if self.provider == "gcp":
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(storage_key)
            blob.delete()
        elif self.provider == "aws":
            self.client.delete_object(Bucket=self.bucket_name, Key=storage_key)
        elif self.provider == "local":
            file_path = os.path.join(self.local_storage_path, storage_key)
            if os.path.exists(file_path):
                os.remove(file_path)

        logger.info(f"Deleted file from {self.provider}: {storage_key}")
