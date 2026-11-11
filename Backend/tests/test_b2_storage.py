from pathlib import Path
from unittest.mock import Mock

from app.services.b2_storage import B2Storage

def test_storage_uses_b2_s3_credentials_and_endpoint(monkeypatch):
    client = Mock()
    client_factory = Mock(return_value=client)
    monkeypatch.setattr("app.services.b2_storage.boto3.client", client_factory)
    monkeypatch.setenv("B2_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("B2_ENDPOINT_URL", "https://s3.us-west-004.backblazeb2.com")
    monkeypatch.setenv("B2_KEY_ID", "test-key-id")
    monkeypatch.setenv("B2_APPLICATION_KEY", "test-application-key")
    monkeypatch.delenv("B2_REGION", raising=False)

    storage = B2Storage()

    client_factory.assert_called_once()
    assert client_factory.call_args.kwargs["aws_access_key_id"] == "test-key-id"
    assert client_factory.call_args.kwargs["region_name"] == "us-west-004"
    assert storage.bucket_name == "test-bucket"

def test_storage_upload_download_and_delete(monkeypatch, tmp_path: Path):
    client = Mock()
    monkeypatch.setattr("app.services.b2_storage.boto3.client", Mock(return_value=client))
    monkeypatch.setenv("B2_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("B2_ENDPOINT_URL", "https://s3.us-west-004.backblazeb2.com")
    monkeypatch.setenv("B2_KEY_ID", "test-key-id")
    monkeypatch.setenv("B2_APPLICATION_KEY", "test-application-key")
    monkeypatch.delenv("B2_REGION", raising=False)

    storage = B2Storage()
    source = tmp_path / "document.pdf"
    source.write_bytes(b"test pdf")
    with source.open("rb") as file_obj:
        object_key = storage.upload_file(file_obj, r"C:\uploads\document.pdf")

    assert object_key.startswith("documents/")
    assert object_key.endswith("/document.pdf")
    upload_args = client.upload_fileobj.call_args
    assert upload_args.args[1:] == ("test-bucket", object_key)
    assert upload_args.kwargs["ExtraArgs"] == {"ContentType": "application/pdf"}

    destination = tmp_path / "download.pdf"
    storage.download_to_path(object_key, destination)
    client.download_file.assert_called_once_with(
        "test-bucket", object_key, str(destination)
    )
    storage.delete_file(object_key)
    client.delete_object.assert_called_once_with(
        Bucket="test-bucket", Key=object_key
    )


def test_storage_reports_missing_configuration(monkeypatch):
    for name in (
        "B2_BUCKET_NAME",
        "B2_ENDPOINT_URL",
        "B2_KEY_ID",
        "B2_APPLICATION_KEY",
    ):
        monkeypatch.delenv(name, raising=False)

    try:
        B2Storage()
    except RuntimeError as error:
        assert "B2_BUCKET_NAME" in str(error)
    else:
        raise AssertionError("Missing B2 configuration should fail explicitly")
