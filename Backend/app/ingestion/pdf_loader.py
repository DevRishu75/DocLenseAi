import fitz
from app.services.ocr_service import OCRService
class PDFLoader:
    ''' Loading pdf and extracting text from pdf'''
    OCR_TEXT_THRESHOLD = 20
    def __init__(self):
        self.ocr_service = OCRService()
    def extract_text(self,file_path:str)->list[dict]:
        document = fitz.open(file_path)
        pages = []
        for page_number,page in enumerate(document,start=1):
            text = page.get_text("text",sort=True).strip()
            print(f"PAGE : {page_number}:"
                  f"PyMuPdf text : {text[:50]}..."
                  f"PyMuPdf characters : {len(text)}")
            
            
            if len(text)>=self.OCR_TEXT_THRESHOLD:
                extracted_text=text
                print(
                f"PAGE {page_number}: Using normal PDF text extraction"
            )
            else:
                extracted_text = self._extract_with_ocr(
                    page
                )
                print(
                f"PAGE {page_number}: Using OCR, "
                f"OCR characters = {len(extracted_text.strip())}",
            )
                print("EXTRACTED PREVIEW:", repr(extracted_text[:100]))
            pages.append({
                    "text":extracted_text,
                    "page_number":page_number
                }
                )
            print(f"PAGE {page_number}: PDF rotation = {page.rotation}")
        document.close()
        return pages
    def _extract_with_ocr(self,page)->str:
        pixmap = page.get_pixmap(
            matrix = fitz.Matrix(2,2)
        )
        image_bytes = pixmap.tobytes("png")
        return self.ocr_service.extract_text_from_image(image_bytes)