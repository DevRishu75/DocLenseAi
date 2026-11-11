import os
import tempfile
import uuid
from pathlib import Path, PurePosixPath

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.chunking.chunker import Chunker
from app.core.logging import logger
from app.exception_handling.upload_exception import UploadDocumentError
from app.ingestion.pdf_loader import PDFLoader
from app.ingestion.text_cleaner import TextCleaner
from app.models.document_model import Document
from app.models.user_model import User
from app.services.b2_storage import B2Storage
from app.services.embedding_service import EmbeddingService
from app.storage.vectorstore import VectorStore


class FileService:
    """Validate, persist, and index uploaded PDF documents."""

    CHUNK_SIZE = 1024 * 1024

    def __init__(self) -> None:
        self.pdf_loader = PDFLoader()
        self.text_cleaner = TextCleaner()
        self.chunker = Chunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.storage: B2Storage | None = None

    def _copy_upload(self, file: UploadFile, destination: Path) -> int:
        max_size_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
        if max_size_mb < 1:
            raise RuntimeError("MAX_UPLOAD_SIZE_MB must be a positive integer")
        max_size = max_size_mb * 1024 * 1024

        file.file.seek(0)
        total_size = 0
        first_chunk = True
        with destination.open("wb") as output:
            while chunk := file.file.read(self.CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > max_size:
                    raise UploadDocumentError(
                        message=f"PDF exceeds the {max_size_mb} MB upload limit",
                        status_code=413,
                        error_code="UPLOAD_TOO_LARGE",
                    )
                if first_chunk:
                    first_chunk = False
                    if not chunk.startswith(b"%PDF-"):
                        raise UploadDocumentError(
                            message="The uploaded file is not a valid PDF",
                            status_code=415,
                            error_code="INVALID_FILE_TYPE",
                        )
                output.write(chunk)

        if total_size == 0:
            raise UploadDocumentError(
                message="The uploaded PDF is empty",
                status_code=422,
                error_code="EMPTY_FILE",
            )
        return total_size

    def _cleanup(
        self,
        db: Session,
        object_key: str | None,
        document_id: str | None,
        vectors_may_exist: bool,
    ) -> None:
        db.rollback()
        if vectors_may_exist and document_id:
            try:
                self.vector_store.delete_document(document_id)
            except Exception:
                logger.exception(
                    "Could not remove vectors after failed upload",
                    extra={"document_id": document_id},
                )
        if object_key and self.storage:
            try:
                self.storage.delete_file(object_key)
            except Exception:
                logger.exception(
                    "Could not remove Backblaze object after failed upload",
                    extra={"storage_key": object_key},
                )

    def process_pdf(self, file: UploadFile, db: Session, current_user: User) -> dict:
        original_filename = PurePosixPath(
            (file.filename or "").replace("\\", "/")
        ).name
        if not original_filename or Path(original_filename).suffix.lower() != ".pdf":
            raise UploadDocumentError(
                message="Please upload a PDF file",
                status_code=415,
                error_code="INVALID_FILE_TYPE",
            )

        object_key = None
        document_id = str(uuid.uuid4())
        vectors_may_exist = False
        try:
            try:
                storage = B2Storage()
                self.storage = storage
            except RuntimeError as error:
                logger.error("Backblaze B2 configuration is incomplete: %s", error)
                raise UploadDocumentError(
                    message="Backblaze B2 storage is not configured",
                    status_code=503,
                    error_code="UPLOAD_STORAGE_CONFIG_ERROR",
                ) from error

            with tempfile.TemporaryDirectory(prefix="doclense-upload-") as temp_dir:
                saved_path = Path(temp_dir) / "document.pdf"
                self._copy_upload(file, saved_path)

                pages = self.pdf_loader.extract_text(str(saved_path))
                cleaned_pages = self.text_cleaner.clean(pages)
                chunks = self.chunker.chunk(cleaned_pages)
                if not chunks:
                    raise UploadDocumentError(
                        message="No readable text was found in the PDF",
                        status_code=422,
                        error_code="EMPTY_DOCUMENT",
                    )

                chunk_text = [chunk["text"] for chunk in chunks]
                embeddings = self.embedding_service.embed_chunks(chunk_text)
                ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
                metadatas = [
                    {
                        "document_id": document_id,
                        "source": original_filename,
                        "chunk_index": i,
                        "page_number": chunk["page_number"],
                    }
                    for i, chunk in enumerate(chunks)
                ]
                
                with saved_path.open("rb") as file_obj:
                    object_key = storage.upload_file(
                        file_obj,
                        original_filename,
                        "application/pdf",
                    )

                document = Document(
                    id=uuid.UUID(document_id),
                    filename=original_filename,
                    user_id=current_user.user_id,
                    storage_key=object_key,
                )
                db.add(document)
                db.flush()

                vectors_may_exist = True
                self.vector_store.add_document(ids, chunk_text, metadatas, embeddings)
                db.commit()
                db.refresh(document)

                logger.info(
                    "Document uploaded and indexed",
                    extra={
                        "document_id": document_id,
                        "chunk_count": len(chunks),
                    },
                )
                return {
                    "document_id": document_id,
                    "filename": original_filename,
                    "text_length": sum(len(page["text"]) for page in cleaned_pages),
                    "text_preview": cleaned_pages[0]["text"][:1000]
                    if cleaned_pages
                    else "",
                    "message": "PDF processed successfully",
                }
        except UploadDocumentError:
            self._cleanup(db, object_key, document_id, vectors_may_exist)
            raise
        except (BotoCoreError, ClientError) as error:
            logger.exception(
                "Backblaze B2 operation failed",
                extra={"document_id": document_id},
            )
            self._cleanup(db, object_key, document_id, vectors_may_exist)
            raise UploadDocumentError(
                message="Unable to store the PDF in Backblaze B2",
                status_code=503,
                error_code="UPLOAD_STORAGE_ERROR",
            ) from error
        except Exception as error:
            logger.exception(
                "Document processing failed",
                extra={"document_id": document_id},
            )
            self._cleanup(db, object_key, document_id, vectors_may_exist)
            raise UploadDocumentError(
                message="Error while processing document",
                status_code=422,
                error_code="UPLOAD_DOCUMENT_ERROR",
            ) from error
