import pytesseract

from PIL import Image
from io import BytesIO
from app.exception_handling.ocr_exception import OCRExceptionError

class OCRService:
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    def __init__(self):
        try:
            pytesseract.pytesseract.tesseract_cmd = self.TESSERACT_PATH
        except Exception as error:
            raise OCRExceptionError(
                message="OCR Service Initialization failure",
                status_code=500,
                error_code="OCR_INITIALIZATION_ERROR"
            )from error
    def extract_text_from_image(self,image_bytes:bytes)->str:
            try:
                image = Image.open(
                    BytesIO(image_bytes)
                )
                text = pytesseract.image_to_string(image)
                return text
            except Exception as error:
                raise OCRExceptionError(
                    message="Failed to extract text from image",
                    status_code=500,
                    error_code="OCR_EXTRACTION_ERROR"
                )from error