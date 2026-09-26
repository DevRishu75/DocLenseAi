from pathlib import Path
from fastapi import UploadFile
import shutil
from sqlalchemy.orm import Session
from app.ingestion.pdf_loader import PDFLoader
from app.ingestion.text_cleaner import TextCleaner
from app.chunking.chunker import Chunker
from app.services.embedding_service import EmbeddingService
from app.storage.vectorstore import VectorStore
from app.models.document_model import Document
from app.models.user_model import User
from app.exception_handling.upload_exception import UploadDocumentError
from app.core.logging import logger
# print(PDFLoader)
class FileService:# Blueprint for creating FileService objects
    """Handles all the files related to --
       Responsibilities
       Save uploaded files
       process pdf documents"""

    UPLOAD_FOLDER = Path("uploads") # class variable every FileService object shares it knows about 
    def __init__(self):   #method that a class can perform 
        self.UPLOAD_FOLDER.mkdir(exist_ok=True)

        self.pdf_loader = PDFLoader()   # Create a PDFLoader object and store it as an attribute
        # of this FileService instance.
        self.text_cleaner = TextCleaner()
        self.chunker = Chunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
    def save_uploaded_file(self, file:UploadFile) ->Path: #Method of an object means object can do this 

        file_path = self.UPLOAD_FOLDER/file.filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file,buffer)
        
        return file_path
    def process_pdf(self,file:UploadFile,db:Session,current_user:User)->dict:
        #step 1: save file
        try:
            
                    saved_path = self.save_uploaded_file(file)
                 
                    print(f"Saved path : {saved_path}")
                    logger.info("File saved successfully",
                                extra={
                                     "filename":file.filename,
                                     "file_path":file.str(saved_path)
                                })
                    
                    #Extracted raw text
                    # raw_text = self.pdf_loader.extract_text(str(saved_path))
                    #Extract_pages 
                    pages = self.pdf_loader.extract_text(str(saved_path))
                    logger.info(
                      "PDF text extracted",
                               extra={
                                 "page_count": len(pages)
                     }
                  )
                    # Clean text while preserving page numbers
                    cleaned_pages = self.text_cleaner.clean(pages)
                    # chunking the cleaned pages
                    chunks = self.chunker.chunk(cleaned_pages)
        except Exception as error:
             logger.exception("Document Processing Failed")
             raise UploadDocumentError(
                  message="Error while processing document",
                  status_code=422,
                  error_code="UPLOAD_DOCUMENT_ERROR"
             )from error
     
        # print("CHUNK COUNT:", len(chunks))
        logger.info(
             "Chunks created ",
             extra={
                  "result_count":len(chunks)
             }
        )
        # print(type(chunks))
        # print(chunks)
        # print(f"chunks created : {len(chunks)}")
        chunk_text = [
             chunk["text"]
             for chunk in chunks
        ]
        embeddings = self.embedding_service.embed_chunks(chunk_text)
        # print(f"embeddings generated : {len(embeddings)}")
        logger.info("Embeddings Created Successfully",
                    extra={
                         "result_embeddings":len(embeddings)
                    })

        # Create : PostgreSQL document--
        document = Document(
            filename = file.filename,
            user_id = current_user.user_id
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        document_id = str(document.id)
        ids = [
            f"{document_id}_chunk_{i}"
            for i in range(len(chunks))
        ]
        metadatas = [        #variables (attributes) a object(class) knows about 
            {
                "document_id":document_id,
                "source": file.filename,
                "chunk_index": i,
                "page_number":chunk["page_number"]
            }
            for i,chunk in enumerate(chunks)
        ]
        logger.info(
             "Document Processed",
             extra={
                  "document_id":str(document.id),
                  "chunk_count":len(chunks)
             }
        )
        self.vector_store.add_document(ids,chunk_text,metadatas,embeddings)
        logger.info(
        "Vectors stored successfully",
        extra={
            "document_id": document_id,
            "vector_count": len(chunk_text)
        }
      )
        print("Stored vectors:", self.vector_store.collection.count())

        #step 4: Return Result
         # Step 10: Return result
        return {
        "document_id": document_id,
        "filename": file.filename,
        "file_path": str(saved_path),
        "text_length": sum(
            len(page["text"])
            for page in cleaned_pages
        ),
        "text_preview": cleaned_pages[0]["text"][:1000]
        if cleaned_pages
        else "",
        "message": "PDF processed successfully"
       }