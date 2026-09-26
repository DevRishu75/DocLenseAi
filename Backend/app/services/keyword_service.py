
class KeywordSearch:
    def search(self,question:str,chunks:list[str]):
        keywords = question.lower().split()
        results = []

        for index,chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            score = 0
            for keyword in keywords:
                if keyword in chunk_lower:
                    score+=1
            results.append(
                {   "index":index,
                    "chunk":chunk,
                    "keyword_score": score
                }
            )
        results.sort(
            key=lambda item:item['keyword_score'],
            reverse = True
        )
        return results