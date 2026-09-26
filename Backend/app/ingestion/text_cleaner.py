import re

class TextCleaner:
    ''' Cleaning text that was extracted'''

    def clean(self,pages:list[dict])->list[dict]:

        # clean_text = re.sub(r"\s+", " ", text)
        # clean_text = clean_text.strip()
        cleaned_pages = []
        for page in pages:
            clean_text = re.sub(
                r"\s+",
                " ",
                page["text"]
            )
            clean_text = clean_text.strip()
            cleaned_pages.append({
                "text":clean_text,
                "page_number":page["page_number"]
            })
        return cleaned_pages
