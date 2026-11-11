import os
import uuid
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

class B2Storage:
    def __init__(self) -> None:
        required = {
            "B2_BUCKET_NAME": os.getenv("B2_BUCKET_NAME", "").strip(),
            "B2_ENDPOINT_URL": os.getenv("B2_ENDPOINT_URL", "").strip(),
            "B2_KEY_ID": os.getenv("B2_KEY_ID", "").strip(),
            "B2_APPLICATION_KEY": os.getenv("B2_APPLICATION_KEY", "").strip(),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                f"Missing required Backblaze B2 configuration: {', '.join(missing)}"
            )
        self.bucket_name = required["B2_BUCKET_NAME"]
        endpoint_url = required["B2_ENDPOINT_URL"].rstrip("/")
        endpoint_host = urlparse(endpoint_url).hostname
        if not endpoint_host:
            raise RuntimeError("B2_ENDPOINT_URL must be a valid S3 endpoint URL")
        region = os.getenv("B2_REGION", "").strip() or None
        if not region:
            host_parts = endpoint_host.split(".")
            region = host_parts[1] if len(host_parts) > 1 and host_parts[0] == "s3" else None
        if not region:
            raise RuntimeError(
                "Set B2_REGION or use a regional B2 S3 endpoint such as "
                "https://s3.us-west-004.backblazeb2.com"
            )
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=required["B2_KEY_ID"],
            aws_secret_access_key=required["B2_APPLICATION_KEY"],
            region_name=region,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                retries={"max_attempts": 3, "mode": "standard"},
            ),
        )
    def upload_file(
        self,
        file_obj,
        original_filename: str,
        content_type: str = "application/pdf",
    ) -> str:
        """Upload a file object and return its unique B2 object key."""
        filename = PurePosixPath(original_filename.replace("\\", "/")).name
        object_key = f"documents/{uuid.uuid4().hex}/{filename}"
        self.client.upload_fileobj(
            file_obj,
            self.bucket_name,
            object_key,
            ExtraArgs={"ContentType": content_type},
        )
        return object_key
    def download_to_path(self, object_key: str, destination: Path) -> None:
        """Download a stored object to a local path."""
        self.client.download_file(
            self.bucket_name,
            object_key,
            str(destination),
        )

    def delete_file(self, object_key: str) -> None:
        """Delete a stored object from B2."""
        self.client.delete_object(Bucket=self.bucket_name, Key=object_key)


# Keep the original class name available for existing local integrations.
B2storage = B2Storage
