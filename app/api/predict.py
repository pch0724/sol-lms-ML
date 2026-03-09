from fastapi import APIRouter
from app.schemas.input import PredictRequest
from app.services.inference_service import predict_dropout
from typing import List
from app.schemas.dropout_risk import DropoutRiskOutput

router = APIRouter(prefix="/predict", tags=["predict"])

# @router.post("")
# def predict(req: StudentInput):
#     prob = predict_dropout(req)
#     return {"dropout_probability": prob}
@router.post("", response_model=List[DropoutRiskOutput])
def predict(req: PredictRequest):
    
    result = predict_dropout(req)

    return result or []