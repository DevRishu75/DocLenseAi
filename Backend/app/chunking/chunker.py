from typing import List
from app.chunking.strategies import SplitterFactory

class Chunker:
      """
    Coordinates the chunking process.

    Responsibilities:
    - Get the appropriate splitting strategy.
    - Split cleaned text into chunks.
    - Return a list of chunks.
    """
      def __init__(self, strategy:str = "character"):
            self.splitter = SplitterFactory.get_splitter(strategy)
      def chunk(self,pages:list[dict])->List[dict]:
            chunks =[]
            for page in pages:
                  page_chunks = self.splitter.split(page["text"])
            for chunk in page_chunks:
                  chunks.append({
                        "text":chunk,
                        "page_number":page["page_number"]
                  })
            '''converted clean text into chunk'''
            return chunks    