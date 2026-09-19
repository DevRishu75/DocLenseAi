
class RelevanceService:
    def is_relevant(self,distance:float,threshold:float=1.5)->bool:
        return distance<=threshold
    def calculate_score(self,distance:float)->float:
        score = 1/(1+distance)
        return round(score,4)