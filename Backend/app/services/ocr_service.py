import os

import pytesseract

from PIL import Image
from io import BytesIO
from app.exception_handling.ocr_exception import OCRExceptionError

class OCRService:
    def __init__(self):
        configured_path = os.getenv("TESSERACT_CMD")
        if configured_path:
            pytesseract.pytesseract.tesseract_cmd = configured_path
    def extract_text_from_image(self,image_bytes:bytes)->str:
            try:
                image = Image.open(
                    BytesIO(image_bytes)
                ).convert("RGB")
                try:
                     osd = pytesseract.image_to_osd(image,config="--psm 0")
                     import re 
                     match = re.search(r"Rotate:\s+(\d+)", osd)
                     if match:
                          rotation = int(match.group(1))%360
                          if rotation:
                            image = image.rotate(-rotation,expand=True)
                except pytesseract.TesseractError:
                    pass
                text = pytesseract.image_to_string(image)
                return text
            except Exception as error:
                raise OCRExceptionError(
                    message="Failed to extract text from image",
                    status_code=500,
                    error_code="OCR_EXTRACTION_ERROR"
                )from error