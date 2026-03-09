from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    training_id: int = Field(alias="trainingId")
    trainee_key_allowed: int = Field(alias="traineeKeyAllowed")

    class Config:
        populate_by_name = True