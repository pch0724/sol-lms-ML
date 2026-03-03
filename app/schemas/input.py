from pydantic import BaseModel

class PredictRequest(BaseModel):
    trainingId: int