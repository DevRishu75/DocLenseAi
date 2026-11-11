"""Explicit Backblaze B2 smoke test; run with `python tests/test_b2_connection.py`."""

import uuid

from app.services.b2_storage import B2Storage


def main() -> None:
    storage = B2Storage()
    object_key = f"documents/connection-tests/{uuid.uuid4().hex}.txt"
    payload = b"DocLense AI Backblaze connection test"
    uploaded = False
    try:
        storage.client.put_object(
            Bucket=storage.bucket_name,
            Key=object_key,
            Body=payload,
            ContentType="text/plain",
        )
        uploaded = True
        response = storage.client.get_object(
            Bucket=storage.bucket_name,
            Key=object_key,
        )
        body = response["Body"]
        try:
            actual = body.read()
        finally:
            body.close()
        if actual != payload:
            raise RuntimeError("Backblaze smoke test returned unexpected content")
        print("Backblaze upload and download succeeded.")
    finally:
        if uploaded:
            storage.delete_file(object_key)

if __name__ == "__main__":
    main()
