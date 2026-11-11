from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
from fastapi import UploadFile

from app.exception_handling.upload_exception import UploadDocumentError
from app.services import file_service as file_service_module
from app.services.file_service import FileService

def make_service():
    service = object.__new__(FileService)
    service.pdf_loader = Mock()
    service.pdf_loader.extract_text.return_value = [
        {"text": "A test document with readable text.", "page_number": 1}
    ]
    service.text_cleaner = Mock()
    service.text_cleaner.clean.side_effect = lambda pages: pages
    service.chunker = Mock()
    service.chunker.chunk.return_value = [
        {"text": "A test document with readable text.", "page_number": 1}
    ]
    service.embedding_service = Mock()
    service.embedding_service.embed_chunks.return_value = [[0.1, 0.2]]
    service.vector_store = Mock()
    service.storage = None
    return service

def make_upload():
    return UploadFile(
        filename="document.pdf",
        file=BytesIO(b"%PDF-1.7 test content"),
    )

def test_process_pdf_stores_object_key_with_document(monkeypatch):
    storage = Mock()
    storage.upload_file.return_value = "documents/example/document.pdf"
    monkeypatch.setattr(
        file_service_module,
        "B2Storage",
        Mock(return_value=storage),
    )
    service = make_service()
    db = Mock()
    user_id = uuid4()

    result = service.process_pdf(make_upload(), db, SimpleNamespace(user_id=user_id))

    assert result["filename"] == "document.pdf"
    assert UUID(result["document_id"])
    document = db.add.call_args.args[0]
    assert document.user_id == user_id
    assert document.storage_key == "documents/example/document.pdf"
    storage.upload_file.assert_called_once()
    service.vector_store.add_document.assert_called_once()
    db.commit.assert_called_once()

def test_process_pdf_removes_cloud_object_when_indexing_fails(monkeypatch):
    storage = Mock()
    storage.upload_file.return_value = "documents/example/document.pdf"
    monkeypatch.setattr(
        file_service_module,
        "B2Storage",
        Mock(return_value=storage),
    )
    service = make_service()
    service.vector_store.add_document.side_effect = RuntimeError("index unavailable")
    db = Mock()

    with pytest.raises(UploadDocumentError) as error:
        service.process_pdf(make_upload(), db, SimpleNamespace(user_id=uuid4()))

    assert error.value.error_code == "UPLOAD_DOCUMENT_ERROR"
    storage.delete_file.assert_called_once_with("documents/example/document.pdf")
    service.vector_store.delete_document.assert_called_once()
    db.rollback.assert_called_once()
